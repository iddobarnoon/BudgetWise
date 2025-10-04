import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.models import BudgetPlan, CategoryAllocation, BudgetSummary, Category
from shared.database import db


class BudgetEngine:
    """Generates and manages personalized budgets"""

    async def create_budget(
        self,
        user_id: str,
        month: str,
        income: Decimal,
        goals: List[str] = None
    ) -> BudgetPlan:
        """
        Generate monthly budget using:
        - User income
        - Historical spending patterns
        - Category priorities (from Ranking System)
        - Financial goals (save X%, pay off debt, etc.)
        """
        goals = goals or []

        # Get categories with priorities
        categories = await db.get_categories(include_custom=False)
        user_prefs = await db.get_user_category_preferences(user_id)
        pref_map = {pref["category_id"]: pref for pref in user_prefs}

        # Get historical spending patterns (last 3 months)
        expenses = await db.get_user_expense_history(user_id, limit=200)
        spending_patterns = self._analyze_spending_patterns(expenses)

        # Determine allocation strategy based on goals
        allocation_strategy = self._determine_allocation_strategy(goals)

        # Calculate allocations for each category
        allocations = []
        total_allocated = Decimal("0")

        # Sort categories by priority (necessity score + user preferences)
        sorted_categories = sorted(
            categories,
            key=lambda c: pref_map.get(c["id"], {}).get("custom_priority", c["necessity_score"]),
            reverse=True
        )

        for cat in sorted_categories:
            cat_id = cat["id"]

            # Calculate allocation amount
            if cat_id in pref_map and pref_map[cat_id].get("monthly_limit"):
                allocated_amount = Decimal(str(pref_map[cat_id]["monthly_limit"]))
            else:
                # Use default percentage or historical average
                if cat_id in spending_patterns:
                    allocated_amount = spending_patterns[cat_id]["avg_monthly"]
                else:
                    percentage = Decimal(str(cat["default_allocation_percent"])) / 100
                    allocated_amount = income * percentage * allocation_strategy.get(cat["name"], Decimal("1"))

            # Apply allocation strategy adjustments
            allocated_amount = self._apply_strategy_adjustments(
                allocated_amount,
                cat,
                allocation_strategy
            )

            allocations.append(CategoryAllocation(
                category_id=cat_id,
                allocated_amount=allocated_amount,
                spent_amount=Decimal("0"),
                remaining_amount=allocated_amount
            ))
            total_allocated += allocated_amount

        # Adjust if over/under budget
        if total_allocated > income:
            allocations = self._rebalance_allocations(allocations, income, sorted_categories)

        # Create budget in database
        budget_data = {
            "user_id": user_id,
            "month": month,
            "total_income": str(income),
        }

        budget_response = await self._save_budget_to_db(budget_data, allocations)

        budget_plan = BudgetPlan(
            id=budget_response["id"],
            user_id=user_id,
            month=month,
            total_income=income,
            allocations=allocations,
            created_at=datetime.fromisoformat(budget_response["created_at"]),
            updated_at=datetime.fromisoformat(budget_response["updated_at"])
        )

        return budget_plan

    async def check_purchase(
        self,
        user_id: str,
        amount: Decimal,
        category_id: str,
        month: str
    ) -> Dict[str, Any]:
        """
        Validate if purchase fits budget
        Returns: {
            "fits_budget": bool,
            "remaining_in_category": Decimal,
            "percentage_of_category": float,
            "alternative_options": List[str]
        }
        """
        # Get budget allocation for this category
        budget = await self._get_budget_allocation(user_id, category_id, month)

        if not budget:
            return {
                "fits_budget": False,
                "remaining_in_category": Decimal("0"),
                "percentage_of_category": 0.0,
                "alternative_options": ["Create a budget for this month first"],
                "warning": "No budget found for this month"
            }

        remaining = Decimal(str(budget["allocated_amount"])) - Decimal(str(budget["spent_amount"]))
        percentage = (float(amount) / float(budget["allocated_amount"]) * 100) if budget["allocated_amount"] > 0 else 0

        fits_budget = amount <= remaining

        alternatives = []
        if not fits_budget:
            overage = amount - remaining
            alternatives = [
                f"Wait until next month when budget resets",
                f"Reduce purchase amount by ${overage:.2f} to stay in budget",
                f"Reallocate ${overage:.2f} from another category"
            ]

            # Suggest categories with surplus
            surplus_categories = await self._find_surplus_categories(user_id, month)
            if surplus_categories:
                alternatives.append(f"Consider using funds from: {', '.join(surplus_categories)}")

        return {
            "fits_budget": fits_budget,
            "remaining_in_category": remaining,
            "percentage_of_category": round(percentage, 2),
            "alternative_options": alternatives,
            "warning": f"This exceeds your budget by ${amount - remaining:.2f}" if not fits_budget else None
        }

    async def get_budget_summary(
        self,
        user_id: str,
        month: str
    ) -> BudgetSummary:
        """Get current budget state with spending breakdown"""
        budget = await self._get_budget_by_month(user_id, month)

        if not budget:
            return BudgetSummary(
                total_budget=Decimal("0"),
                total_spent=Decimal("0"),
                total_remaining=Decimal("0"),
                categories=[],
                overspent_categories=[]
            )

        allocations_data = budget.get("allocations", [])
        allocations = []
        total_spent = Decimal("0")
        total_budget = Decimal("0")
        overspent = []

        for alloc in allocations_data:
            allocated = Decimal(str(alloc["allocated_amount"]))
            spent = Decimal(str(alloc["spent_amount"]))
            remaining = allocated - spent

            allocations.append(CategoryAllocation(
                category_id=alloc["category_id"],
                allocated_amount=allocated,
                spent_amount=spent,
                remaining_amount=remaining
            ))

            total_budget += allocated
            total_spent += spent

            if spent > allocated:
                overspent.append(alloc["category_id"])

        return BudgetSummary(
            total_budget=total_budget,
            total_spent=total_spent,
            total_remaining=total_budget - total_spent,
            categories=allocations,
            overspent_categories=overspent
        )

    async def update_spent_amount(
        self,
        user_id: str,
        category_id: str,
        amount: Decimal,
        month: str
    ) -> CategoryAllocation:
        """Update spent amount when expense is logged"""
        allocation = await self._get_budget_allocation(user_id, category_id, month)

        if not allocation:
            raise ValueError(f"No budget allocation found for category {category_id} in {month}")

        new_spent = Decimal(str(allocation["spent_amount"])) + amount
        new_remaining = Decimal(str(allocation["allocated_amount"])) - new_spent

        # Update in database
        updated = await self._update_allocation_spent(
            allocation["id"],
            new_spent
        )

        return CategoryAllocation(
            category_id=category_id,
            allocated_amount=Decimal(str(updated["allocated_amount"])),
            spent_amount=new_spent,
            remaining_amount=new_remaining
        )

    async def suggest_reallocation(
        self,
        user_id: str,
        month: str
    ) -> List[Dict[str, Any]]:
        """
        Suggest budget adjustments based on spending patterns
        e.g., "You're overspending on dining, reallocate from entertainment?"
        """
        summary = await self.get_budget_summary(user_id, month)
        suggestions = []

        # Find overspent and underspent categories
        overspent = []
        underspent = []

        for alloc in summary.categories:
            if alloc.spent_amount > alloc.allocated_amount:
                overspent.append(alloc)
            elif alloc.remaining_amount > alloc.allocated_amount * Decimal("0.5"):  # More than 50% remaining
                underspent.append(alloc)

        # Generate suggestions
        for over_alloc in overspent:
            overage = over_alloc.spent_amount - over_alloc.allocated_amount

            for under_alloc in underspent:
                available = under_alloc.remaining_amount

                if available >= overage:
                    cat_over = await db.get_category_by_id(over_alloc.category_id)
                    cat_under = await db.get_category_by_id(under_alloc.category_id)

                    suggestions.append({
                        "type": "reallocation",
                        "from_category": cat_under["name"],
                        "to_category": cat_over["name"],
                        "amount": float(overage),
                        "reason": f"You've overspent on {cat_over['name']} by ${overage:.2f}, "
                                 f"but have ${available:.2f} remaining in {cat_under['name']}"
                    })

        return suggestions

    # Helper methods

    def _analyze_spending_patterns(self, expenses: List[Dict[str, Any]]) -> Dict[str, Dict[str, Decimal]]:
        """Analyze historical spending to calculate averages per category"""
        patterns = {}

        for expense in expenses:
            cat_id = expense.get("category_id")
            if not cat_id:
                continue

            if cat_id not in patterns:
                patterns[cat_id] = {"total": Decimal("0"), "count": 0}

            patterns[cat_id]["total"] += Decimal(str(expense["amount"]))
            patterns[cat_id]["count"] += 1

        # Calculate averages
        for cat_id in patterns:
            total = patterns[cat_id]["total"]
            count = patterns[cat_id]["count"]
            patterns[cat_id]["avg_monthly"] = total / max(count, 1)

        return patterns

    def _determine_allocation_strategy(self, goals: List[str]) -> Dict[str, Decimal]:
        """Determine multipliers based on financial goals"""
        strategy = {}

        for goal in goals:
            goal_lower = goal.lower()

            if "save" in goal_lower or "emergency fund" in goal_lower:
                strategy["Savings"] = Decimal("1.5")  # Increase savings allocation
                strategy["Entertainment"] = Decimal("0.7")  # Reduce discretionary
                strategy["Dining Out"] = Decimal("0.7")

            elif "debt" in goal_lower or "pay off" in goal_lower:
                strategy["Debt Payments"] = Decimal("1.5")
                strategy["Entertainment"] = Decimal("0.5")
                strategy["Travel"] = Decimal("0.5")

            elif "invest" in goal_lower:
                strategy["Savings"] = Decimal("1.3")

        return strategy

    def _apply_strategy_adjustments(
        self,
        amount: Decimal,
        category: Dict[str, Any],
        strategy: Dict[str, Decimal]
    ) -> Decimal:
        """Apply strategy multipliers to allocation amounts"""
        multiplier = strategy.get(category["name"], Decimal("1"))
        return amount * multiplier

    def _rebalance_allocations(
        self,
        allocations: List[CategoryAllocation],
        income: Decimal,
        categories: List[Dict[str, Any]]
    ) -> List[CategoryAllocation]:
        """Rebalance allocations to fit within income"""
        total = sum(a.allocated_amount for a in allocations)

        if total == 0:
            return allocations

        ratio = income / total

        rebalanced = []
        for alloc in allocations:
            rebalanced.append(CategoryAllocation(
                category_id=alloc.category_id,
                allocated_amount=alloc.allocated_amount * ratio,
                spent_amount=Decimal("0"),
                remaining_amount=alloc.allocated_amount * ratio
            ))

        return rebalanced

    async def _save_budget_to_db(
        self,
        budget_data: Dict[str, Any],
        allocations: List[CategoryAllocation]
    ) -> Dict[str, Any]:
        """Save budget and allocations to database"""
        # Insert budget
        budget_response = await db.client.table("budgets").insert(budget_data).execute()
        budget = budget_response.data[0]

        # Insert allocations
        for alloc in allocations:
            await db.client.table("budget_allocations").insert({
                "budget_id": budget["id"],
                "category_id": alloc.category_id,
                "allocated_amount": str(alloc.allocated_amount),
                "spent_amount": str(alloc.spent_amount)
            }).execute()

        return budget

    async def _get_budget_allocation(
        self,
        user_id: str,
        category_id: str,
        month: str
    ) -> Optional[Dict[str, Any]]:
        """Get budget allocation for a specific category"""
        budget = await self._get_budget_by_month(user_id, month)

        if not budget:
            return None

        response = await db.client.table("budget_allocations").select("*").eq(
            "budget_id", budget["id"]
        ).eq("category_id", category_id).execute()

        return response.data[0] if response.data else None

    async def _get_budget_by_month(
        self,
        user_id: str,
        month: str
    ) -> Optional[Dict[str, Any]]:
        """Get budget for a specific month"""
        response = await db.client.table("budgets").select("*").eq(
            "user_id", user_id
        ).eq("month", month).execute()

        budget = response.data[0] if response.data else None

        if budget:
            # Fetch allocations
            alloc_response = await db.client.table("budget_allocations").select("*").eq(
                "budget_id", budget["id"]
            ).execute()
            budget["allocations"] = alloc_response.data

        return budget

    async def _update_allocation_spent(
        self,
        allocation_id: str,
        new_spent: Decimal
    ) -> Dict[str, Any]:
        """Update spent amount for an allocation"""
        response = await db.client.table("budget_allocations").update({
            "spent_amount": str(new_spent)
        }).eq("id", allocation_id).execute()

        return response.data[0]

    async def _find_surplus_categories(
        self,
        user_id: str,
        month: str
    ) -> List[str]:
        """Find categories with significant remaining budget"""
        summary = await self.get_budget_summary(user_id, month)
        surplus = []

        for alloc in summary.categories:
            if alloc.remaining_amount > alloc.allocated_amount * Decimal("0.5"):
                cat = await db.get_category_by_id(alloc.category_id)
                if cat:
                    surplus.append(cat["name"])

        return surplus


# Global budget engine instance
budget_engine = BudgetEngine()
