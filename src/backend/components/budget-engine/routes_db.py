from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from decimal import Decimal
import sys
from pathlib import Path
import os
from datetime import datetime
import uuid

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Create Supabase client
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

router = APIRouter(prefix="/budget", tags=["budget"])

# Request/Response Models

class CreateBudgetRequest(BaseModel):
    user_id: str
    month: str
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
    warning: Optional[str] = None

class UpdateSpentRequest(BaseModel):
    user_id: str
    category_id: str
    amount: Decimal
    month: str

# Endpoints

@router.post("/create")
async def create_budget(request: CreateBudgetRequest):
    """
    Generate monthly budget using categories from database
    """
    try:
        # Check if budget already exists
        existing_budget = supabase.table('budgets').select('*').eq('user_id', request.user_id).eq('month', request.month).execute()
        if existing_budget.data:
            raise HTTPException(status_code=400, detail=f"Budget for {request.month} already exists. Use update endpoint instead.")

        # Get all categories
        categories_result = supabase.table('categories').select('*').order('necessity_score', desc=True).execute()
        categories = categories_result.data

        if not categories:
            raise HTTPException(status_code=404, detail="No categories found. Please seed the database.")

        # Apply 50/30/20 rule
        income = float(request.income)
        needs_budget = income * 0.50
        wants_budget = income * 0.30
        savings_budget = income * 0.20

        # Categorize (ensure no duplicates)
        savings_names = ['Savings', 'Emergency Fund', 'Investments']
        savings_cats = [c for c in categories if c['name'] in savings_names]
        needs = [c for c in categories if c['necessity_score'] >= 8 and c['name'] not in savings_names]
        wants = [c for c in categories if 4 <= c['necessity_score'] < 8 and c['name'] not in savings_names]

        # Create budget record
        budget_data = {
            "user_id": request.user_id,
            "month": request.month,
            "total_income": str(request.income)
        }

        budget_result = supabase.table('budgets').insert(budget_data).execute()
        budget = budget_result.data[0]

        # Create allocations
        allocations = []

        # Distribute needs budget
        if needs:
            per_need = needs_budget / len(needs)
            for cat in needs:
                allocations.append({
                    "budget_id": budget['id'],
                    "category_id": cat['id'],
                    "allocated_amount": str(round(per_need, 2)),
                    "spent_amount": "0"
                })

        # Distribute wants budget
        if wants:
            per_want = wants_budget / len(wants)
            for cat in wants:
                allocations.append({
                    "budget_id": budget['id'],
                    "category_id": cat['id'],
                    "allocated_amount": str(round(per_want, 2)),
                    "spent_amount": "0"
                })

        # Savings
        if savings_cats:
            per_savings = savings_budget / len(savings_cats)
            for cat in savings_cats:
                allocations.append({
                    "budget_id": budget['id'],
                    "category_id": cat['id'],
                    "allocated_amount": str(round(per_savings, 2)),
                    "spent_amount": "0"
                })

        # Insert allocations
        if allocations:
            supabase.table('budget_allocations').insert(allocations).execute()

        return {
            "status": "success",
            "budget_id": budget['id'],
            "user_id": request.user_id,
            "month": request.month,
            "total_income": float(request.income),
            "allocations_count": len(allocations),
            "strategy": "50/30/20 Rule",
            "goals": request.goals
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check-purchase", response_model=CheckPurchaseResponse)
async def check_purchase(request: CheckPurchaseRequest):
    """
    Validate if purchase fits budget by checking database
    """
    try:
        # Get budget for this month
        budget_result = supabase.table('budgets').select('*').eq(
            'user_id', request.user_id
        ).eq('month', request.month).execute()

        if not budget_result.data:
            return CheckPurchaseResponse(
                fits_budget=False,
                remaining_in_category=Decimal("0"),
                percentage_of_category=0.0,
                alternative_options=["Create a budget for this month first"],
                warning="No budget found for this month"
            )

        budget = budget_result.data[0]

        # Get allocation for this category
        alloc_result = supabase.table('budget_allocations').select('*').eq(
            'budget_id', budget['id']
        ).eq('category_id', request.category_id).execute()

        if not alloc_result.data:
            return CheckPurchaseResponse(
                fits_budget=False,
                remaining_in_category=Decimal("0"),
                percentage_of_category=0.0,
                alternative_options=["This category is not in your budget"],
                warning="Category not found in budget"
            )

        allocation = alloc_result.data[0]
        allocated = Decimal(str(allocation['allocated_amount']))
        spent = Decimal(str(allocation['spent_amount']))
        remaining = allocated - spent

        fits = request.amount <= remaining
        percentage = (float(request.amount) / float(allocated) * 100) if allocated > 0 else 0

        alternatives = []
        if not fits:
            overage = request.amount - remaining
            alternatives = [
                "Wait until next month when budget resets",
                f"Reduce purchase by ${overage:.2f} to stay in budget"
            ]

        return CheckPurchaseResponse(
            fits_budget=fits,
            remaining_in_category=remaining,
            percentage_of_category=round(percentage, 2),
            alternative_options=alternatives,
            warning=f"Exceeds budget by ${request.amount - remaining:.2f}" if not fits else None
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def get_budget_summary(user_id: str, month: str):
    """
    Get budget summary from database
    """
    try:
        # Get budget
        budget_result = supabase.table('budgets').select('*').eq(
            'user_id', user_id
        ).eq('month', month).execute()

        if not budget_result.data:
            raise HTTPException(status_code=404, detail="Budget not found")

        budget = budget_result.data[0]

        # Get allocations with category names
        alloc_result = supabase.table('budget_allocations').select(
            '*, categories(name)'
        ).eq('budget_id', budget['id']).execute()

        allocations = alloc_result.data

        total_allocated = sum(Decimal(str(a['allocated_amount'])) for a in allocations)
        total_spent = sum(Decimal(str(a['spent_amount'])) for a in allocations)
        total_remaining = total_allocated - total_spent

        overspent = [a for a in allocations if Decimal(str(a['spent_amount'])) > Decimal(str(a['allocated_amount']))]

        return {
            "budget_id": budget['id'],
            "month": month,
            "total_budget": float(total_allocated),
            "total_spent": float(total_spent),
            "total_remaining": float(total_remaining),
            "categories": [
                {
                    "category_id": a['category_id'],
                    "category_name": a['categories']['name'],
                    "allocated": float(a['allocated_amount']),
                    "spent": float(a['spent_amount']),
                    "remaining": float(Decimal(str(a['allocated_amount'])) - Decimal(str(a['spent_amount'])))
                }
                for a in allocations
            ],
            "overspent_categories": [a['categories']['name'] for a in overspent]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update-spent")
async def update_spent_amount(request: UpdateSpentRequest):
    """
    Update spent amount when expense is logged
    """
    try:
        # Get budget
        budget_result = supabase.table('budgets').select('*').eq(
            'user_id', request.user_id
        ).eq('month', request.month).execute()

        if not budget_result.data:
            raise HTTPException(status_code=404, detail="Budget not found")

        budget = budget_result.data[0]

        # Get allocation
        alloc_result = supabase.table('budget_allocations').select('*').eq(
            'budget_id', budget['id']
        ).eq('category_id', request.category_id).execute()

        if not alloc_result.data:
            raise HTTPException(status_code=404, detail="Category allocation not found")

        allocation = alloc_result.data[0]

        # Update spent amount
        new_spent = Decimal(str(allocation['spent_amount'])) + request.amount

        update_result = supabase.table('budget_allocations').update({
            "spent_amount": str(new_spent)
        }).eq('id', allocation['id']).execute()

        updated = update_result.data[0]

        return {
            "category_id": request.category_id,
            "allocated_amount": float(updated['allocated_amount']),
            "spent_amount": float(updated['spent_amount']),
            "remaining_amount": float(Decimal(str(updated['allocated_amount'])) - Decimal(str(updated['spent_amount'])))
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/suggestions")
async def get_reallocation_suggestions(user_id: str, month: str) -> List[Dict[str, Any]]:
    """
    Get budget reallocation suggestions
    """
    try:
        # Get budget summary
        summary = await get_budget_summary(user_id, month)

        suggestions = []

        # Find overspent and underspent categories
        overspent = []
        underspent = []

        for cat in summary['categories']:
            if cat['spent'] > cat['allocated']:
                overspent.append(cat)
            elif cat['remaining'] > cat['allocated'] * 0.5:
                underspent.append(cat)

        # Generate suggestions
        for over_cat in overspent:
            overage = over_cat['spent'] - over_cat['allocated']

            for under_cat in underspent:
                available = under_cat['remaining']

                if available >= overage:
                    suggestions.append({
                        "type": "reallocation",
                        "from_category": under_cat['category_name'],
                        "to_category": over_cat['category_name'],
                        "amount": overage,
                        "reason": f"You've overspent on {over_cat['category_name']} by ${overage:.2f}, "
                                 f"but have ${available:.2f} remaining in {under_cat['category_name']}"
                    })

        return suggestions

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
