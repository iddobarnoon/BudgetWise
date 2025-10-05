from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from decimal import Decimal
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/ranking", tags=["ranking"])

# Initialize Supabase
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

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


async def match_merchant_to_category(merchant: str, user_id: str) -> tuple[Optional[str], float]:
    """Match merchant to category using rules and user overrides"""
    normalized = normalize_merchant(merchant)

    # Check user overrides first
    try:
        override_result = supabase.table('user_merchant_overrides').select('category_id').eq('user_id', user_id).eq('merchant_name', normalized).execute()
        if override_result.data:
            return override_result.data[0]['category_id'], 0.99
    except Exception as e:
        print(f"Error checking overrides: {e}")

    # Get all categories with their rules
    categories_result = supabase.table('categories').select('id, name, necessity_score').execute()
    categories = categories_result.data

    scores = []
    for category in categories:
        rules = await get_category_rules(category['id'])
        category_score = 0

        for rule in rules:
            # Simple keyword matching
            if rule['merchant_pattern'].lower() in normalized:
                category_score += rule['weight']

        scores.append({
            'category_id': category['id'],
            'category_name': category['name'],
            'necessity_score': category['necessity_score'],
            'score': category_score
        })

    # Sort by score
    scores.sort(key=lambda x: x['score'], reverse=True)

    if not scores or scores[0]['score'] == 0:
        return None, 0.0

    # Calculate confidence
    score_values = [s['score'] for s in scores]
    confidence = calculate_confidence(score_values)

    return scores[0]['category_id'], confidence


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
async def classify_expense(request: ClassifyExpenseRequest) -> ClassifyExpenseResponse:
    """
    Classify expense and return category with confidence
    """
    try:
        merchant = request.merchant or request.description
        category_id, confidence = await match_merchant_to_category(merchant, request.user_id)

        if not category_id:
            # Default to uncategorized or first category
            categories_result = supabase.table('categories').select('*').limit(1).execute()
            if categories_result.data:
                category = categories_result.data[0]
                return ClassifyExpenseResponse(
                    category_id=category['id'],
                    category_name=category['name'],
                    necessity_score=category['necessity_score'],
                    confidence=0.3,
                    alternatives=[]
                )
            raise HTTPException(status_code=404, detail="No categories found")

        # Get the matched category
        category_result = supabase.table('categories').select('*').eq('id', category_id).execute()
        category = category_result.data[0]

        # Get alternatives (top 3)
        all_categories = supabase.table('categories').select('*').execute()
        alternatives = [
            {"category_id": c['id'], "category_name": c['name'], "confidence": 0.3}
            for c in all_categories.data[:3] if c['id'] != category_id
        ]

        return ClassifyExpenseResponse(
            category_id=category['id'],
            category_name=category['name'],
            necessity_score=category['necessity_score'],
            confidence=confidence,
            alternatives=alternatives
        )
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
        category_id, confidence = await match_merchant_to_category(merchant, request.user_id)

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
