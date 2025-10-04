from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from decimal import Decimal
import sys
from pathlib import Path

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from main import budget_engine
from shared.models import BudgetPlan, BudgetSummary, CategoryAllocation

router = APIRouter(prefix="/budget", tags=["budget"])

# Request/Response Models

class CreateBudgetRequest(BaseModel):
    user_id: str
    month: str  # Format: "2025-10"
    income: Decimal
    goals: List[str] = []

class CheckPurchaseRequest(BaseModel):
    user_id: str
    amount: Decimal
    category_id: str
    month: str

class CheckPurchaseResponse(BaseModel):
    fits_budget: bool
    remaining_in_category: Decimal
    percentage_of_category: float
    alternative_options: List[str]
    warning: str = None

class UpdateSpentRequest(BaseModel):
    user_id: str
    category_id: str
    amount: Decimal
    month: str

# Endpoints

@router.post("/create", response_model=BudgetPlan)
async def create_budget(request: CreateBudgetRequest):
    """
    Generate monthly budget using:
    - User income
    - Historical spending patterns
    - Category priorities (from Ranking System)
    - Financial goals
    """
    try:
        budget_plan = await budget_engine.create_budget(
            user_id=request.user_id,
            month=request.month,
            income=request.income,
            goals=request.goals
        )
        return budget_plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check-purchase", response_model=CheckPurchaseResponse)
async def check_purchase(request: CheckPurchaseRequest):
    """
    Validate if purchase fits budget
    Returns budget status and alternatives if over budget
    """
    try:
        result = await budget_engine.check_purchase(
            user_id=request.user_id,
            amount=request.amount,
            category_id=request.category_id,
            month=request.month
        )
        return CheckPurchaseResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary", response_model=BudgetSummary)
async def get_budget_summary(user_id: str, month: str):
    """
    Get current budget state with spending breakdown
    Shows total budget, spent, remaining, and overspent categories
    """
    try:
        summary = await budget_engine.get_budget_summary(
            user_id=user_id,
            month=month
        )
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update-spent", response_model=CategoryAllocation)
async def update_spent_amount(request: UpdateSpentRequest):
    """
    Update spent amount when expense is logged
    Automatically updates remaining budget
    """
    try:
        allocation = await budget_engine.update_spent_amount(
            user_id=request.user_id,
            category_id=request.category_id,
            amount=request.amount,
            month=request.month
        )
        return allocation
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/suggestions")
async def get_reallocation_suggestions(user_id: str, month: str) -> List[Dict[str, Any]]:
    """
    Suggest budget adjustments based on spending patterns
    e.g., "You're overspending on dining, reallocate from entertainment?"
    """
    try:
        suggestions = await budget_engine.suggest_reallocation(
            user_id=user_id,
            month=month
        )
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
