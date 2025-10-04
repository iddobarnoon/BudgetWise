class RankingSystem:
    def normalize_merchant(raw_merchant: str) -> str:
        """
        Normalize merchant names for consistent matching.
        Removes punctuation, numbers, and converts to lowercase.
        Example: "Trader Joe's #122" → "trader joes"
        """
        pass


    def apply_user_overrides(user_id: str, normalized_merchant: str) -> str | None:
        """
        Check if the user has manually assigned a category for this merchant before.
        If yes, return that category_id immediately; otherwise return None.
        """
        pass


    def compute_match_score(normalized_merchant: str, rule: dict) -> float:
        """
        Compute similarity between the merchant name and a given category rule.
        Uses string comparison (exact, substring, regex).
        Returns a score between 0 and 1.
        """
        pass


    def rank_categories(user_id: str, merchant: str, amount: float) -> dict:
        """
        Rank all possible categories for a purchase.

        Steps:
        1. Normalize merchant.
        2. Apply user overrides.
        3. Evaluate each rule using compute_match_score().
        4. Sort by score and return best match + confidence.

        Returns:
            {
                "best_category": "Dining Out",
                "confidence": 0.92,
                "alternatives": [("Groceries", 0.7), ("Shopping", 0.5)]
            }
        """
        pass


    def update_confidence(scores: list[float]) -> float:
        """
        Calculate confidence based on difference between the top two scores.
        Example: conf = (top - second) / top
        Returns a float between 0 and 1.
        """
        pass


    def save_ranking_result(expense_id: str, category_id: str, confidence: float) -> None:
        """
        Save the ranked category result for an expense into the database.
        Includes confidence and possibly the rule trace for explainability.
        """
        pass


    def handle_correction(user_id: str, merchant: str, correct_category_id: str) -> None:
        """
        Handle user corrections when a category was wrong.
        Update user_overrides so that next time, the correct category is auto-selected.
        """
        pass


    def process_expense_for_ranking(expense: dict) -> dict:
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
        pass
