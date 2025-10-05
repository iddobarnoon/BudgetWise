"""
Orchestrator for coordinating calls between AI, Budget Engine, and Ranking System
"""

import os
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime
from decimal import Decimal
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class ServiceOrchestrator:
    """
    Coordinates calls between multiple microservices:
    - Budget Engine (port 8003)
    - Ranking System (port 8002)
    - AI Service (internal)
    """

    def __init__(self):
        self.budget_engine_url = os.getenv("BUDGET_ENGINE_URL", "http://localhost:8003")
        self.ranking_service_url = os.getenv("RANKING_SERVICE_URL", "http://localhost:8002")
        self.timeout = httpx.Timeout(30.0, connect=5.0)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5)
    )
    async def _call_service(
        self,
        method: str,
        url: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generic service call with retry logic

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full URL to call
            json_data: JSON payload for POST/PUT
            params: Query parameters

        Returns:
            Response JSON data
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    json=json_data,
                    params=params
                )
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                logger.error(f"Service call failed: {e.response.status_code} - {e.response.text}")
                raise
            except httpx.RequestError as e:
                logger.error(f"Request error: {str(e)}")
                raise

    # ============= Ranking System Calls =============

    async def classify_expense(
        self,
        description: str,
        amount: float,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Classify expense using Ranking System

        Returns:
            {
                "category": {...},
                "confidence": 0.95,
                "alternatives": [...]
            }
        """
        try:
            url = f"{self.ranking_service_url}/ranking/classify"
            data = {
                "description": description,
                "amount": amount,
                "user_id": user_id
            }
            result = await self._call_service("POST", url, json_data=data)
            return result

        except Exception as e:
            logger.error(f"Expense classification failed: {e}")
            # Fallback to default category
            return {
                "category": {
                    "id": "unknown",
                    "name": "Uncategorized",
                    "necessity_score": 5
                },
                "confidence": 0.0,
                "alternatives": []
            }

    async def get_categories(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all categories with user preferences

        Returns:
            List of categories
        """
        try:
            url = f"{self.ranking_service_url}/ranking/categories"
            params = {"user_id": user_id}
            result = await self._call_service("GET", url, params=params)
            return result.get("categories", [])

        except Exception as e:
            logger.error(f"Failed to fetch categories: {e}")
            return []

    async def get_priority_order(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get categories ordered by priority

        Returns:
            List of categories in priority order
        """
        try:
            url = f"{self.ranking_service_url}/ranking/priorities"
            params = {"user_id": user_id}
            result = await self._call_service("GET", url, params=params)
            return result.get("priorities", [])

        except Exception as e:
            logger.error(f"Failed to fetch priorities: {e}")
            return []

    # ============= Budget Engine Calls =============

    async def check_purchase(
        self,
        user_id: str,
        amount: float,
        category_id: str,
        month: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check if purchase fits within budget

        Returns:
            {
                "fits_budget": bool,
                "remaining_in_category": float,
                "percentage_of_category": float,
                "alternative_options": [...]
            }
        """
        try:
            if not month:
                month = datetime.now().strftime("%Y-%m")

            url = f"{self.budget_engine_url}/budget/check-purchase"
            data = {
                "user_id": user_id,
                "amount": amount,
                "category_id": category_id,
                "month": month
            }
            result = await self._call_service("POST", url, json_data=data)
            return result

        except Exception as e:
            logger.error(f"Budget check failed: {e}")
            # Fallback response
            return {
                "fits_budget": False,
                "remaining_in_category": 0,
                "percentage_of_category": 0,
                "alternative_options": ["Unable to verify budget at this time"]
            }

    async def get_budget_summary(
        self,
        user_id: str,
        month: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get current budget summary

        Returns:
            BudgetSummary with categories and spending
        """
        try:
            if not month:
                month = datetime.now().strftime("%Y-%m")

            url = f"{self.budget_engine_url}/budget/summary"
            params = {"user_id": user_id, "month": month}
            result = await self._call_service("GET", url, params=params)
            return result

        except Exception as e:
            logger.error(f"Failed to fetch budget summary: {e}")
            return {
                "total_budget": 0,
                "total_spent": 0,
                "total_remaining": 0,
                "categories": [],
                "overspent_categories": []
            }

    async def create_budget(
        self,
        user_id: str,
        month: str,
        income: float,
        goals: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new budget for the user

        Returns:
            Created budget plan
        """
        try:
            url = f"{self.budget_engine_url}/budget/create"
            data = {
                "user_id": user_id,
                "month": month,
                "income": income,
                "goals": goals or []
            }
            result = await self._call_service("POST", url, json_data=data)
            return result

        except Exception as e:
            logger.error(f"Budget creation failed: {e}")
            raise

    async def update_spent_amount(
        self,
        user_id: str,
        category_id: str,
        amount: float,
        month: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update spent amount when expense is logged

        Returns:
            Updated category allocation
        """
        try:
            if not month:
                month = datetime.now().strftime("%Y-%m")

            url = f"{self.budget_engine_url}/budget/update-spent"
            data = {
                "user_id": user_id,
                "category_id": category_id,
                "amount": amount,
                "month": month
            }
            result = await self._call_service("PUT", url, json_data=data)
            return result

        except Exception as e:
            logger.error(f"Failed to update spent amount: {e}")
            raise

    # ============= Orchestrated Workflows =============

    async def analyze_purchase_decision(
        self,
        user_id: str,
        user_message: str,
        item: str,
        amount: float
    ) -> Dict[str, Any]:
        """
        Complete purchase analysis workflow:
        1. Classify category (Ranking System)
        2. Check budget (Budget Engine)
        3. Get user profile
        4. Return all context for AI analysis

        Returns:
            Complete context for AI purchase decision
        """
        # Step 1: Classify the item
        classification = await self.classify_expense(
            description=item,
            amount=amount,
            user_id=user_id
        )

        # Extract from flat structure (ranking system returns flat, not nested)
        category_id = classification.get("category_id")
        category_name = classification.get("category_name", "Unknown")
        necessity_score = classification.get("necessity_score", 5)

        # Step 2: Check budget
        budget_check = await self.check_purchase(
            user_id=user_id,
            amount=amount,
            category_id=category_id
        )

        # Step 3: Build context
        context = {
            "classification": classification,
            "category": category_name,
            "category_id": category_id,
            "necessity_score": necessity_score,
            "budget_context": {
                "fits_budget": budget_check.get("fits_budget", False),
                "category_budget": budget_check.get("category_budget", 0),
                "spent_amount": budget_check.get("spent_amount", 0),
                "remaining_amount": budget_check.get("remaining_in_category", 0)
            },
            "item": item,
            "amount": amount,
            "user_message": user_message
        }

        return context

    async def log_expense_workflow(
        self,
        user_id: str,
        description: str,
        amount: float,
        date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete expense logging workflow:
        1. Classify category
        2. Update budget spent amount
        3. Return logged expense

        Returns:
            Expense details with category and budget update
        """
        # Step 1: Classify
        classification = await self.classify_expense(
            description=description,
            amount=amount,
            user_id=user_id
        )

        category = classification.get("category", {})
        category_id = category.get("id")

        # Step 2: Update budget
        try:
            await self.update_spent_amount(
                user_id=user_id,
                category_id=category_id,
                amount=amount
            )
        except Exception as e:
            logger.warning(f"Could not update budget: {e}")

        # Step 3: Return result
        return {
            "description": description,
            "amount": amount,
            "category": category.get("name"),
            "category_id": category_id,
            "confidence": classification.get("confidence", 0),
            "date": date or datetime.now().isoformat()
        }

    async def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """
        Get complete user context for AI:
        - Current budget status
        - Recent expenses
        - Category preferences

        Returns:
            Complete user context
        """
        try:
            # Get budget summary
            budget_summary = await self.get_budget_summary(user_id)

            # Get categories
            categories = await self.get_categories(user_id)

            return {
                "budget_summary": budget_summary,
                "categories": categories,
                "user_id": user_id
            }

        except Exception as e:
            logger.error(f"Failed to get user context: {e}")
            return {
                "budget_summary": {},
                "categories": [],
                "user_id": user_id
            }


# Global orchestrator instance
orchestrator = ServiceOrchestrator()
