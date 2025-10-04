import re
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from decimal import Decimal

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.models import Category, CategoryRule, RankingResult, CategoryMatch
from shared.database import db
from shared.utils import normalize_merchant, calculate_confidence_from_scores


class RankingSystem:
    """Service for categorizing and ranking expenses by necessity"""

    def __init__(self):
        self.category_rules: List[Dict[str, Any]] = []
        self.categories_cache: Dict[str, Category] = {}

    async def initialize(self):
        """Load categories and rules into memory"""
        # Load categories
        categories = await db.get_categories(include_custom=False)
        self.categories_cache = {cat["id"]: Category(**cat) for cat in categories}

        # Load category rules
        self.category_rules = await db.get_category_rules()

    async def apply_user_overrides(self, user_id: str, normalized_merchant: str) -> Optional[str]:
        """
        Check if the user has manually assigned a category for this merchant before.
        If yes, return that category_id immediately; otherwise return None.
        """
        category_id = await db.get_user_override(user_id, normalized_merchant)
        return category_id

    def compute_match_score(self, normalized_merchant: str, rule: Dict[str, Any]) -> float:
        """
        Compute similarity between the merchant name and a given category rule.
        Uses string comparison (exact, substring, regex).
        Returns a score between 0 and 1.
        """
        match_type = rule.get("match_type", "substring")
        keywords = rule.get("keywords", [])
        merchant_patterns = rule.get("merchant_patterns", [])
        priority = rule.get("priority", 0)

        max_score = 0.0

        # Check keywords
        for keyword in keywords:
            keyword_lower = keyword.lower()

            if match_type == "exact":
                if normalized_merchant == keyword_lower:
                    max_score = max(max_score, 1.0)
            elif match_type == "substring":
                if keyword_lower in normalized_merchant:
                    # Longer matches get higher scores
                    match_ratio = len(keyword_lower) / len(normalized_merchant)
                    max_score = max(max_score, min(match_ratio * 1.5, 1.0))
            elif match_type == "regex":
                try:
                    if re.search(keyword_lower, normalized_merchant, re.IGNORECASE):
                        max_score = max(max_score, 0.9)
                except re.error:
                    pass

        # Check merchant patterns (exact merchant names)
        for pattern in merchant_patterns:
            pattern_lower = pattern.lower()
            if pattern_lower in normalized_merchant or normalized_merchant in pattern_lower:
                similarity = len(set(normalized_merchant.split()) & set(pattern_lower.split())) / max(
                    len(normalized_merchant.split()), len(pattern_lower.split())
                )
                max_score = max(max_score, similarity)

        # Apply priority boost (0-10 scale, boost by up to 0.1)
        priority_boost = priority * 0.01
        final_score = min(max_score + priority_boost, 1.0)

        return final_score

    async def rank_categories(
        self,
        user_id: str,
        merchant: str,
        amount: float,
        description: Optional[str] = None
    ) -> RankingResult:
        """
        Rank all possible categories for a purchase.

        Steps:
        1. Normalize merchant.
        2. Apply user overrides.
        3. Evaluate each rule using compute_match_score().
        4. Sort by score and return best match + confidence.
        """
        # Step 1: Normalize merchant
        normalized = normalize_merchant(merchant)

        # Step 2: Check user overrides
        override_category_id = await self.apply_user_overrides(user_id, normalized)
        if override_category_id and override_category_id in self.categories_cache:
            return RankingResult(
                best_category=self.categories_cache[override_category_id],
                confidence=1.0,
                alternatives=[]
            )

        # Step 3: Evaluate all rules
        category_scores: Dict[str, float] = {}

        for rule in self.category_rules:
            score = self.compute_match_score(normalized, rule)
            category_id = rule["category_id"]

            if category_id not in category_scores:
                category_scores[category_id] = score
            else:
                # Keep highest score for each category
                category_scores[category_id] = max(category_scores[category_id], score)

        # Check description for additional matching
        if description:
            normalized_desc = normalize_merchant(description)
            for rule in self.category_rules:
                desc_score = self.compute_match_score(normalized_desc, rule)
                category_id = rule["category_id"]
                # Blend merchant and description scores
                if category_id in category_scores:
                    category_scores[category_id] = max(category_scores[category_id], desc_score * 0.8)
                else:
                    category_scores[category_id] = desc_score * 0.8

        # Step 4: Sort and get best match
        if not category_scores:
            # Default to "Other" category
            other_cat = next((cat for cat in self.categories_cache.values() if cat.name.lower() == "other"), None)
            if other_cat:
                return RankingResult(
                    best_category=other_cat,
                    confidence=0.3,
                    alternatives=[]
                )

        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        best_category_id, best_score = sorted_categories[0]

        # Calculate confidence
        scores = [score for _, score in sorted_categories]
        confidence = calculate_confidence_from_scores(scores)

        # Get alternatives (top 3 excluding best)
        alternatives = [
            (self.categories_cache[cat_id].name, score)
            for cat_id, score in sorted_categories[1:4]
            if cat_id in self.categories_cache
        ]

        return RankingResult(
            best_category=self.categories_cache[best_category_id],
            confidence=confidence,
            alternatives=alternatives
        )

    async def save_ranking_result(self, expense_id: str, category_id: str, confidence: float) -> None:
        """
        Save the ranked category result for an expense into the database.
        Includes confidence and possibly the rule trace for explainability.
        """
        await db.update_expense_category(expense_id, category_id, confidence)

    async def handle_correction(self, user_id: str, merchant: str, correct_category_id: str) -> None:
        """
        Handle user corrections when a category was wrong.
        Update user_overrides so that next time, the correct category is auto-selected.
        """
        normalized = normalize_merchant(merchant)
        await db.save_user_override(user_id, normalized, correct_category_id)

    async def process_expense_for_ranking(self, expense: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main public entry point.
        Receives an expense dictionary, runs through the full ranking pipeline:
        - normalization
        - user overrides
        - category ranking
        - confidence calculation
        - database save

        Returns the final ranked result dictionary.
        """
        user_id = expense["user_id"]
        merchant = expense.get("merchant", expense.get("description", ""))
        amount = float(expense.get("amount", 0))
        description = expense.get("description")

        # Ensure categories are loaded
        if not self.categories_cache:
            await self.initialize()

        # Rank categories
        result = await self.rank_categories(user_id, merchant, amount, description)

        # Save result if expense has an ID
        if "id" in expense:
            await self.save_ranking_result(
                expense["id"],
                result.best_category.id,
                result.confidence
            )

        return {
            "expense_id": expense.get("id"),
            "category_id": result.best_category.id,
            "category_name": result.best_category.name,
            "confidence": result.confidence,
            "necessity_score": result.best_category.necessity_score,
            "alternatives": result.alternatives
        }

    async def get_categories(self, user_id: str) -> List[Category]:
        """
        Get all categories with user's custom priorities
        Merges system categories with user preferences
        """
        if not self.categories_cache:
            await self.initialize()

        # Get user preferences
        user_prefs = await db.get_user_category_preferences(user_id)
        pref_map = {pref["category_id"]: pref for pref in user_prefs}

        # Merge with categories
        categories = []
        for cat in self.categories_cache.values():
            # Apply user custom priority if exists
            if cat.id in pref_map:
                # Could extend Category model to include user priority
                pass
            categories.append(cat)

        return categories

    async def get_priority_order(
        self,
        user_id: str,
        budget_constraints: Optional[Dict[str, Any]] = None
    ) -> List[Category]:
        """
        Returns categories ordered by priority for budget allocation
        Factors: necessity_score, user preferences, spending patterns
        """
        categories = await self.get_categories(user_id)

        # Get user preferences
        user_prefs = await db.get_user_category_preferences(user_id)
        pref_map = {pref["category_id"]: pref["custom_priority"] for pref in user_prefs}

        # Sort by priority: user preference > necessity score
        def priority_key(cat: Category):
            user_priority = pref_map.get(cat.id, cat.necessity_score)
            return user_priority

        sorted_categories = sorted(categories, key=priority_key, reverse=True)
        return sorted_categories

    async def update_user_priority(
        self,
        user_id: str,
        category_id: str,
        new_priority: int
    ) -> Dict[str, Any]:
        """Allow users to customize category importance"""
        result = await db.update_user_category_priority(user_id, category_id, new_priority)
        return result


# Global ranking service instance
ranking_service = RankingSystem()
