"""
Budget Allocation Algorithms
Different strategies for distributing income across categories
"""

from decimal import Decimal
from typing import List, Dict, Any
from enum import Enum


class AllocationStrategy(Enum):
    """Available budget allocation strategies"""
    RULE_50_30_20 = "50/30/20"  # 50% needs, 30% wants, 20% savings
    RULE_70_20_10 = "70/20/10"  # 70% expenses, 20% savings, 10% debt
    AGGRESSIVE_SAVE = "aggressive_save"  # Maximize savings
    DEBT_PAYOFF = "debt_payoff"  # Prioritize debt repayment
    BALANCED = "balanced"  # Equal consideration of all categories


class BudgetAlgorithms:
    """Collection of budget allocation algorithms"""

    @staticmethod
    def apply_50_30_20_rule(income: Decimal, categories: List[Dict[str, Any]]) -> Dict[str, Decimal]:
        """
        50/30/20 Budget Rule:
        - 50% Needs (housing, utilities, groceries, healthcare, transportation)
        - 30% Wants (dining, entertainment, shopping, hobbies)
        - 20% Savings (savings, investments, emergency fund)
        """
        needs_budget = income * Decimal("0.50")
        wants_budget = income * Decimal("0.30")
        savings_budget = income * Decimal("0.20")

        # Categorize by type
        needs_categories = []
        wants_categories = []
        savings_categories = []

        for cat in categories:
            necessity = cat.get("necessity_score", 5)
            name = cat.get("name", "").lower()

            if necessity >= 8 or any(word in name for word in ["housing", "utilities", "groceries", "healthcare", "transportation"]):
                needs_categories.append(cat)
            elif "saving" in name or "investment" in name or "emergency" in name:
                savings_categories.append(cat)
            else:
                wants_categories.append(cat)

        # Distribute budgets within each group
        allocations = {}

        # Needs - distribute proportionally by necessity score
        total_needs_score = sum(c.get("necessity_score", 5) for c in needs_categories)
        for cat in needs_categories:
            if total_needs_score > 0:
                ratio = Decimal(str(cat.get("necessity_score", 5))) / Decimal(str(total_needs_score))
                allocations[cat["id"]] = needs_budget * ratio
            else:
                allocations[cat["id"]] = Decimal("0")

        # Wants - distribute evenly or by preference
        if wants_categories:
            per_want = wants_budget / len(wants_categories)
            for cat in wants_categories:
                allocations[cat["id"]] = per_want

        # Savings - prioritize high-necessity savings
        if savings_categories:
            per_saving = savings_budget / len(savings_categories)
            for cat in savings_categories:
                allocations[cat["id"]] = per_saving

        return allocations

    @staticmethod
    def apply_70_20_10_rule(income: Decimal, categories: List[Dict[str, Any]]) -> Dict[str, Decimal]:
        """
        70/20/10 Budget Rule:
        - 70% Living expenses
        - 20% Savings
        - 10% Debt repayment
        """
        living_budget = income * Decimal("0.70")
        savings_budget = income * Decimal("0.20")
        debt_budget = income * Decimal("0.10")

        allocations = {}

        for cat in categories:
            name = cat.get("name", "").lower()

            if "debt" in name or "loan" in name or "credit" in name:
                allocations[cat["id"]] = debt_budget
            elif "saving" in name or "investment" in name:
                allocations[cat["id"]] = savings_budget
            else:
                # Distribute living expenses by default allocation percent
                default_pct = Decimal(str(cat.get("default_allocation_percent", 5))) / 100
                allocations[cat["id"]] = living_budget * default_pct

        return allocations

    @staticmethod
    def aggressive_savings_strategy(income: Decimal, categories: List[Dict[str, Any]]) -> Dict[str, Decimal]:
        """
        Aggressive Savings Strategy:
        - Minimize discretionary spending
        - Maximize savings (aim for 40%+ savings rate)
        """
        allocations = {}

        # Essential categories get normal allocation
        # Discretionary categories get reduced (50% of normal)
        # Savings gets boosted

        savings_total = Decimal("0")
        essential_total = Decimal("0")

        for cat in categories:
            necessity = cat.get("necessity_score", 5)
            name = cat.get("name", "").lower()
            default_pct = Decimal(str(cat.get("default_allocation_percent", 5))) / 100

            if "saving" in name:
                # Boost savings to 40% of income
                allocations[cat["id"]] = income * Decimal("0.40")
                savings_total += allocations[cat["id"]]
            elif necessity >= 8:
                # Essential - full allocation
                allocations[cat["id"]] = income * default_pct
                essential_total += allocations[cat["id"]]
            else:
                # Discretionary - reduce by 50%
                allocations[cat["id"]] = income * default_pct * Decimal("0.5")

        return allocations

    @staticmethod
    def debt_payoff_strategy(income: Decimal, categories: List[Dict[str, Any]]) -> Dict[str, Decimal]:
        """
        Debt Payoff Strategy:
        - Maximize debt payments (avalanche/snowball method)
        - Reduce discretionary to minimum
        - Maintain essentials
        """
        allocations = {}

        debt_total = Decimal("0")

        for cat in categories:
            necessity = cat.get("necessity_score", 5)
            name = cat.get("name", "").lower()
            default_pct = Decimal(str(cat.get("default_allocation_percent", 5))) / 100

            if "debt" in name or "loan" in name or "credit" in name:
                # Aggressive debt payment - 30% of income
                allocations[cat["id"]] = income * Decimal("0.30")
                debt_total += allocations[cat["id"]]
            elif necessity >= 8:
                # Essential - full allocation
                allocations[cat["id"]] = income * default_pct
            else:
                # Discretionary - reduce by 70%
                allocations[cat["id"]] = income * default_pct * Decimal("0.30")

        return allocations

    @staticmethod
    def balanced_strategy(
        income: Decimal,
        categories: List[Dict[str, Any]],
        user_preferences: Dict[str, int] = None
    ) -> Dict[str, Decimal]:
        """
        Balanced Strategy:
        - Uses category necessity scores
        - Applies user preferences if available
        - Distributes proportionally
        """
        user_preferences = user_preferences or {}
        allocations = {}

        # Calculate total priority score
        total_priority = Decimal("0")
        for cat in categories:
            cat_id = cat["id"]
            # Use user preference or necessity score
            priority = user_preferences.get(cat_id, cat.get("necessity_score", 5))
            total_priority += Decimal(str(priority))

        # Distribute income proportionally
        for cat in categories:
            cat_id = cat["id"]
            priority = user_preferences.get(cat_id, cat.get("necessity_score", 5))

            if total_priority > 0:
                ratio = Decimal(str(priority)) / total_priority
                allocations[cat_id] = income * ratio
            else:
                allocations[cat_id] = Decimal("0")

        return allocations

    @staticmethod
    def zero_based_budgeting(
        income: Decimal,
        categories: List[Dict[str, Any]],
        fixed_expenses: Dict[str, Decimal] = None
    ) -> Dict[str, Decimal]:
        """
        Zero-Based Budgeting:
        - Start from zero
        - Allocate every dollar
        - Fixed expenses first, then variable
        """
        fixed_expenses = fixed_expenses or {}
        allocations = {}
        remaining = income

        # Step 1: Allocate fixed expenses
        for cat_id, amount in fixed_expenses.items():
            allocations[cat_id] = amount
            remaining -= amount

        # Step 2: Allocate remaining to variable expenses by priority
        variable_cats = [c for c in categories if c["id"] not in fixed_expenses]
        variable_cats.sort(key=lambda x: x.get("necessity_score", 5), reverse=True)

        for cat in variable_cats:
            default_pct = Decimal(str(cat.get("default_allocation_percent", 5))) / 100
            suggested_amount = income * default_pct

            # Allocate up to remaining budget
            allocated = min(suggested_amount, remaining)
            allocations[cat["id"]] = allocated
            remaining -= allocated

            if remaining <= 0:
                break

        # Step 3: If any remaining, put into savings
        if remaining > 0:
            savings_cat = next((c for c in categories if "saving" in c.get("name", "").lower()), None)
            if savings_cat:
                allocations[savings_cat["id"]] = allocations.get(savings_cat["id"], Decimal("0")) + remaining

        return allocations

    @staticmethod
    def envelope_method(
        income: Decimal,
        categories: List[Dict[str, Any]],
        envelope_limits: Dict[str, Decimal] = None
    ) -> Dict[str, Decimal]:
        """
        Envelope Budgeting Method:
        - Each category gets a fixed "envelope" of cash
        - Once envelope is empty, no more spending
        - Great for controlling discretionary spending
        """
        envelope_limits = envelope_limits or {}
        allocations = {}

        total_envelopes = Decimal("0")

        # Set envelopes based on limits or defaults
        for cat in categories:
            cat_id = cat["id"]

            if cat_id in envelope_limits:
                allocations[cat_id] = envelope_limits[cat_id]
            else:
                default_pct = Decimal(str(cat.get("default_allocation_percent", 5))) / 100
                allocations[cat_id] = income * default_pct

            total_envelopes += allocations[cat_id]

        # Rebalance if over income
        if total_envelopes > income:
            ratio = income / total_envelopes
            for cat_id in allocations:
                allocations[cat_id] *= ratio

        return allocations


def select_strategy(
    goals: List[str],
    income: Decimal,
    categories: List[Dict[str, Any]]
) -> Dict[str, Decimal]:
    """
    Select and apply the best budget strategy based on user goals
    """
    algorithms = BudgetAlgorithms()

    # Parse goals to determine strategy
    goals_lower = [g.lower() for g in goals]

    if any("save" in g or "emergency fund" in g for g in goals_lower):
        return algorithms.aggressive_savings_strategy(income, categories)
    elif any("debt" in g or "pay off" in g for g in goals_lower):
        return algorithms.debt_payoff_strategy(income, categories)
    elif any("50/30/20" in g for g in goals_lower):
        return algorithms.apply_50_30_20_rule(income, categories)
    elif any("70/20/10" in g for g in goals_lower):
        return algorithms.apply_70_20_10_rule(income, categories)
    else:
        # Default to balanced strategy
        return algorithms.balanced_strategy(income, categories)
