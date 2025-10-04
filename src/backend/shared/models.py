from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from decimal import Decimal

# ============= User & Auth =============

class User(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    monthly_income: Decimal
    financial_goals: List[str] = []
    risk_tolerance: Literal["conservative", "moderate", "aggressive"] = "moderate"

class Session(BaseModel):
    user_id: str
    token: str
    expires_at: datetime

# ============= Categories & Ranking =============

class Category(BaseModel):
    id: str
    name: str
    necessity_score: int = Field(..., ge=1, le=10)  # 1=luxury, 10=essential
    default_allocation_percent: float
    parent_category: Optional[str] = None
    is_system: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "id": "cat_001",
                "name": "Groceries",
                "necessity_score": 9,
                "default_allocation_percent": 15.0,
                "is_system": True
            }
        }

class UserCategoryPreference(BaseModel):
    user_id: str
    category_id: str
    custom_priority: int = Field(..., ge=1, le=10)
    monthly_limit: Optional[Decimal] = None

class CategoryRule(BaseModel):
    """Matching rule for categorizing expenses"""
    category_id: str
    keywords: List[str] = []
    merchant_patterns: List[str] = []
    match_type: Literal["exact", "substring", "regex"] = "substring"
    priority: int = 0

class CategoryMatch(BaseModel):
    """Result of category matching"""
    category: Category
    confidence: float = Field(..., ge=0.0, le=1.0)
    match_reason: Optional[str] = None

class RankingResult(BaseModel):
    """Complete ranking result for an expense"""
    best_category: Category
    confidence: float = Field(..., ge=0.0, le=1.0)
    alternatives: List[tuple[str, float]] = []  # (category_name, score)

# ============= Expenses =============

class Expense(BaseModel):
    id: str
    user_id: str
    amount: Decimal
    category_id: str
    description: str
    date: datetime
    is_recurring: bool = False
    ai_suggested_category: Optional[str] = None
    confidence_score: Optional[float] = None

class RecurringExpense(BaseModel):
    id: str
    user_id: str
    amount: Decimal
    category_id: str
    description: str
    frequency: Literal["daily", "weekly", "monthly", "yearly"]
    start_date: datetime
    end_date: Optional[datetime] = None

# ============= Budget =============

class BudgetPlan(BaseModel):
    id: str
    user_id: str
    month: str  # "2025-10"
    total_income: Decimal
    allocations: List["CategoryAllocation"]
    created_at: datetime
    updated_at: datetime

class CategoryAllocation(BaseModel):
    category_id: str
    allocated_amount: Decimal
    spent_amount: Decimal = Decimal("0")
    remaining_amount: Decimal

class BudgetSummary(BaseModel):
    total_budget: Decimal
    total_spent: Decimal
    total_remaining: Decimal
    categories: List[CategoryAllocation]
    overspent_categories: List[str] = []

# ============= AI Responses =============

class PurchaseRecommendation(BaseModel):
    decision: Literal["buy", "wait", "dont_buy"]
    reason: str
    alternative_suggestions: List[str] = []
    impact_on_budget: str
    category: str
    amount: Decimal

class ChatMessage(BaseModel):
    id: str
    user_id: str
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime
    metadata: Optional[dict] = None  # Store expense/budget refs

# Update forward references
BudgetPlan.model_rebuild()
