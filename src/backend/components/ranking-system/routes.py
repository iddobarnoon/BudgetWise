from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from decimal import Decimal

from main import ranking_service
from shared.models import Category

router = APIRouter(prefix="/ranking", tags=["ranking"])

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
    alternatives: List[tuple[str, float]] = []

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

# Endpoints

@router.get("/categories")
async def get_categories(user_id: str) -> List[Category]:
    """
    Get all categories with user's custom priorities
    Merges system categories with user preferences
    """
    try:
        categories = await ranking_service.get_categories(user_id)
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/classify")
async def classify_expense(request: ClassifyExpenseRequest) -> ClassifyExpenseResponse:
    """
    AI-powered expense categorization
    Returns: Category with confidence score
    """
    try:
        # Ensure service is initialized
        if not ranking_service.categories_cache:
            await ranking_service.initialize()

        merchant = request.merchant or request.description
        result = await ranking_service.rank_categories(
            user_id=request.user_id,
            merchant=merchant,
            amount=float(request.amount),
            description=request.description
        )

        return ClassifyExpenseResponse(
            category_id=result.best_category.id,
            category_name=result.best_category.name,
            necessity_score=result.best_category.necessity_score,
            confidence=result.confidence,
            alternatives=result.alternatives
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/priorities")
async def get_priorities(user_id: str) -> List[Category]:
    """
    Returns categories ordered by priority for budget allocation
    Factors: necessity_score, user preferences, spending patterns
    """
    try:
        categories = await ranking_service.get_priority_order(user_id)
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
    Allow users to customize category importance
    """
    try:
        result = await ranking_service.update_user_priority(
            user_id=user_id,
            category_id=category_id,
            new_priority=request.custom_priority
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/correct")
async def correct_category(user_id: str, request: CorrectCategoryRequest) -> Dict[str, str]:
    """
    Handle user corrections when a category was wrong.
    Updates user preferences for future auto-categorization
    """
    try:
        await ranking_service.handle_correction(
            user_id=user_id,
            merchant=request.merchant,
            correct_category_id=request.correct_category_id
        )
        return {"message": "Category preference saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-expense")
async def process_expense(request: ProcessExpenseRequest) -> Dict[str, Any]:
    """
    Main endpoint to process and categorize an expense
    Returns full ranking result with category and confidence
    """
    try:
        expense_data = {
            "user_id": request.user_id,
            "merchant": request.merchant,
            "description": request.description,
            "amount": str(request.amount)
        }

        if request.expense_id:
            expense_data["id"] = request.expense_id

        result = await ranking_service.process_expense_for_ranking(expense_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.on_event("startup")
async def startup_event():
    """Initialize ranking service on startup"""
    await ranking_service.initialize()
