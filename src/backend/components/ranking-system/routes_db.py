from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from decimal import Decimal
import os
import numpy as np
from supabase import create_client
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

router = APIRouter(prefix="/ranking", tags=["ranking"])

# Initialize Supabase
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Initialize OpenAI for embeddings
openai_client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
EMBEDDING_MODEL = "text-embedding-3-small"

# Category embeddings cache (to avoid repeated API calls)
CATEGORY_EMBEDDINGS_CACHE: Dict[str, List[float]] = {}

# Request/Response Models
class ClassifyExpenseRequest(BaseModel):
    description: str
    amount: Decimal
    user_id: str
    merchant: Optional[str] = None

class ClassifyExpenseResponse(BaseModel):
    category_id: str
    category_name: str
    necessity_score: int
    confidence: float
    alternatives: List[Dict[str, Any]] = []

class UpdatePriorityRequest(BaseModel):
    custom_priority: int = Field(..., ge=1, le=10)
    monthly_limit: Optional[Decimal] = None

class CorrectCategoryRequest(BaseModel):
    merchant: str
    correct_category_id: str

class ProcessExpenseRequest(BaseModel):
    user_id: str
    merchant: Optional[str] = None
    description: str
    amount: Decimal
    expense_id: Optional[str] = None


# Helper functions
def normalize_merchant(merchant: str) -> str:
    """Normalize merchant name for matching"""
    import re
    merchant = merchant.lower().strip()
    merchant = re.sub(r'[^\w\s]', '', merchant)  # Remove punctuation
    merchant = re.sub(r'\d+', '', merchant)  # Remove numbers
    merchant = re.sub(r'\s+', ' ', merchant)  # Normalize whitespace
    return merchant.strip()


def calculate_confidence(scores: List[float]) -> float:
    """Calculate confidence based on score gap"""
    if not scores or len(scores) < 2:
        return 0.9

    top_score = scores[0]
    second_score = scores[1]

    if top_score == 0:
        return 0.5

    gap = (top_score - second_score) / top_score
    confidence = min(0.5 + (gap * 0.5), 0.99)
    return round(confidence, 2)


async def get_category_rules(category_id: str) -> List[Dict]:
    """Get rules for a specific category"""
    try:
        result = supabase.table('category_rules').select('*').eq('category_id', category_id).execute()
        return result.data
    except Exception as e:
        print(f"Error fetching rules for category {category_id}: {e}")
        return []


# ============= Semantic Matching Functions =============

async def get_embedding(text: str) -> List[float]:
    """
    Get embedding vector for text using OpenAI

    Args:
        text: Text to embed (merchant name, category name, etc.)

    Returns:
        List of floats representing the embedding vector
    """
    try:
        response = await openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding for '{text}': {e}")
        # Return zero vector as fallback
        return [0.0] * 1536


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Compute cosine similarity between two vectors

    Args:
        vec1: First embedding vector
        vec2: Second embedding vector

    Returns:
        Similarity score between 0 and 1
    """
    # Convert to numpy arrays
    v1 = np.array(vec1)
    v2 = np.array(vec2)

    # Compute cosine similarity
    dot_product = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    similarity = dot_product / (norm1 * norm2)

    # Ensure result is between 0 and 1
    return max(0.0, min(1.0, float(similarity)))


async def get_category_embeddings(categories: List[Dict]) -> Dict[str, List[float]]:
    """
    Get embeddings for all categories (with caching)

    Args:
        categories: List of category dicts with 'id' and 'name' fields

    Returns:
        Dict mapping category_id to embedding vector
    """
    global CATEGORY_EMBEDDINGS_CACHE

    embeddings = {}

    for category in categories:
        category_id = category['id']
        category_name = category['name']

        # Check cache first
        if category_id in CATEGORY_EMBEDDINGS_CACHE:
            embeddings[category_id] = CATEGORY_EMBEDDINGS_CACHE[category_id]
        else:
            # Generate and cache embedding
            embedding = await get_embedding(category_name)
            CATEGORY_EMBEDDINGS_CACHE[category_id] = embedding
            embeddings[category_id] = embedding

    return embeddings


async def match_merchant_to_category(merchant: str, user_id: str) -> tuple[Optional[str], float, List[Dict]]:
    """
    Match merchant to category using semantic embeddings
    Returns: (category_id, confidence, debug_info)
    """
    normalized = normalize_merchant(merchant)
    debug_info = []

    # Check user overrides first (respect explicit user preferences)
    try:
        override_result = supabase.table('user_merchant_overrides').select('category_id').eq('user_id', user_id).eq('merchant_name', normalized).execute()
        if override_result.data:
            debug_info.append({"type": "override", "matched": True, "category_id": override_result.data[0]['category_id']})
            return override_result.data[0]['category_id'], 0.99, debug_info
    except Exception as e:
        print(f"Error checking overrides: {e}")

    # Get all categories
    categories_result = supabase.table('categories').select('id, name, necessity_score').execute()
    categories = categories_result.data

    if not categories:
        return None, 0.0, [{"error": "No categories found"}]

    # Get merchant embedding
    merchant_embedding = await get_embedding(merchant)

    # Get category embeddings (cached)
    category_embeddings = await get_category_embeddings(categories)

    # Compute semantic similarities
    similarities = []
    for category in categories:
        category_id = category['id']
        category_embedding = category_embeddings.get(category_id)

        if not category_embedding:
            continue

        # Calculate cosine similarity
        similarity = cosine_similarity(merchant_embedding, category_embedding)

        similarities.append({
            'category_id': category_id,
            'category_name': category['name'],
            'necessity_score': category['necessity_score'],
            'similarity': similarity
        })

    # Sort by similarity (highest first)
    similarities.sort(key=lambda x: x['similarity'], reverse=True)

    if not similarities:
        return None, 0.0, [{"error": "No similarities computed"}]

    # Get top match
    top_match = similarities[0]
    confidence = top_match['similarity']

    # Build debug info with top 5 matches
    for sim in similarities[:5]:
        debug_info.append({
            "category": sim['category_name'],
            "similarity": round(sim['similarity'], 4),
            "method": "semantic"
        })

    return top_match['category_id'], confidence, debug_info


# Endpoints

@router.get("/categories")
async def get_categories(user_id: str) -> List[Dict[str, Any]]:
    """
    Get all categories with user's custom priorities
    """
    try:
        # Get all categories
        categories_result = supabase.table('categories').select('*').execute()
        categories = categories_result.data

        # Get user preferences
        prefs_result = supabase.table('user_category_preferences').select('*').eq('user_id', user_id).execute()
        user_prefs = {p['category_id']: p for p in prefs_result.data}

        # Merge preferences with categories
        for category in categories:
            if category['id'] in user_prefs:
                pref = user_prefs[category['id']]
                category['custom_priority'] = pref.get('custom_priority')
                category['monthly_limit'] = pref.get('monthly_limit')

        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/classify")
async def classify_expense(request: ClassifyExpenseRequest) -> Dict[str, Any]:
    """
    Classify expense and return category with confidence and debug info
    """
    try:
        merchant = request.merchant or request.description
        category_id, confidence, debug_info = await match_merchant_to_category(merchant, request.user_id)

        if not category_id:
            # This shouldn't happen anymore with improved fallback, but keep as safety
            categories_result = supabase.table('categories').select('*').limit(1).execute()
            if categories_result.data:
                category = categories_result.data[0]
                return {
                    "category_id": category['id'],
                    "category_name": category['name'],
                    "necessity_score": category['necessity_score'],
                    "confidence": 0.3,
                    "alternatives": [],
                    "debug": [{"type": "emergency_fallback", "reason": "match_merchant_to_category returned None"}]
                }
            raise HTTPException(status_code=404, detail="No categories found")

        # Get the matched category
        category_result = supabase.table('categories').select('*').eq('id', category_id).execute()
        category = category_result.data[0]

        # Get alternatives from debug info (next best matches)
        alternatives = [
            {
                "category_name": d['category'],
                "similarity": d['similarity']
            }
            for d in debug_info[1:4] if d.get('category') and d.get('similarity')
        ]

        return {
            "category_id": category['id'],
            "category_name": category['name'],
            "necessity_score": category['necessity_score'],
            "confidence": round(confidence, 4),
            "method": "semantic",
            "alternatives": alternatives,
            "debug": debug_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/priorities")
async def get_priorities(user_id: str) -> List[Dict[str, Any]]:
    """
    Get categories ordered by priority (necessity score + user preferences)
    """
    try:
        # Get all categories
        categories = await get_categories(user_id)

        # Sort by custom_priority if exists, otherwise necessity_score
        def priority_key(cat):
            if cat.get('custom_priority'):
                return (cat['custom_priority'], cat['necessity_score'])
            return (cat['necessity_score'], 0)

        categories.sort(key=priority_key, reverse=True)
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/priorities/{category_id}")
async def update_priority(
    category_id: str,
    user_id: str,
    request: UpdatePriorityRequest
) -> Dict[str, Any]:
    """
    Update user's custom priority for a category
    """
    try:
        # Upsert user preference
        data = {
            "user_id": user_id,
            "category_id": category_id,
            "custom_priority": request.custom_priority,
            "monthly_limit": str(request.monthly_limit) if request.monthly_limit else None
        }

        result = supabase.table('user_category_preferences').upsert(data).execute()

        return {"success": True, "data": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/correct")
async def correct_category(user_id: str, request: CorrectCategoryRequest) -> Dict[str, str]:
    """
    Save user's category correction as a merchant override
    """
    try:
        normalized = normalize_merchant(request.merchant)

        data = {
            "user_id": user_id,
            "merchant_name": normalized,
            "category_id": request.correct_category_id
        }

        supabase.table('user_merchant_overrides').upsert(data).execute()

        return {"message": "Category preference saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process-expense")
async def process_expense(request: ProcessExpenseRequest) -> Dict[str, Any]:
    """
    Process and categorize an expense
    """
    try:
        merchant = request.merchant or request.description
        category_id, confidence, _ = await match_merchant_to_category(merchant, request.user_id)

        if not category_id:
            # Get default category
            categories_result = supabase.table('categories').select('*').limit(1).execute()
            if categories_result.data:
                category = categories_result.data[0]
                category_id = category['id']
                confidence = 0.3

        # Get category details
        category_result = supabase.table('categories').select('*').eq('id', category_id).execute()
        category = category_result.data[0]

        return {
            "category_id": category_id,
            "category_name": category['name'],
            "necessity_score": category['necessity_score'],
            "confidence": confidence,
            "amount": str(request.amount),
            "merchant": merchant
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        supabase.table('categories').select('id').limit(1).execute()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")
