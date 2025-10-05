from supabase import create_client, Client
from typing import Optional, List, Dict, Any
import os
from datetime import datetime
from decimal import Decimal

class SupabaseClient:
    """Wrapper for Supabase database operations"""

    def __init__(self):
        url = os.getenv("SUPABASE_URL", "")
        key = os.getenv("SUPABASE_KEY", "")
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
        self.client: Client = create_client(url, key)

    # ============= Categories =============

    async def get_categories(self, include_custom: bool = False) -> List[Dict[str, Any]]:
        """Get all system categories, optionally including custom ones"""
        query = self.client.table("categories").select("*")
        if not include_custom:
            query = query.eq("is_system", True)
        response = query.execute()
        return response.data

    async def get_category_by_id(self, category_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific category by ID"""
        response = self.client.table("categories").select("*").eq("id", category_id).execute()
        return response.data[0] if response.data else None

    async def get_category_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a category by name (case-insensitive)"""
        response = self.client.table("categories").select("*").ilike("name", name).execute()
        return response.data[0] if response.data else None

    # ============= User Category Preferences =============

    async def get_user_category_preferences(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all category preferences for a user"""
        response = self.client.table("user_category_preferences").select("*").eq("user_id", user_id).execute()
        return response.data

    async def get_user_override(self, user_id: str, merchant: str) -> Optional[str]:
        """Get user's preferred category for a specific merchant"""
        response = (
            self.client.table("user_merchant_overrides")
            .select("category_id")
            .eq("user_id", user_id)
            .eq("merchant", merchant)
            .execute()
        )
        return response.data[0]["category_id"] if response.data else None

    async def save_user_override(self, user_id: str, merchant: str, category_id: str) -> None:
        """Save user's category preference for a merchant"""
        self.client.table("user_merchant_overrides").upsert({
            "user_id": user_id,
            "merchant": merchant,
            "category_id": category_id,
            "updated_at": datetime.utcnow().isoformat()
        }).execute()

    async def update_user_category_priority(
        self,
        user_id: str,
        category_id: str,
        priority: int,
        monthly_limit: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """Update user's custom priority for a category"""
        data = {
            "user_id": user_id,
            "category_id": category_id,
            "custom_priority": priority
        }
        if monthly_limit is not None:
            data["monthly_limit"] = str(monthly_limit)

        response = self.client.table("user_category_preferences").upsert(data).execute()
        return response.data[0]

    # ============= Expenses =============

    async def save_expense(self, expense_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save an expense to the database"""
        response = self.client.table("expenses").insert(expense_data).execute()
        return response.data[0]

    async def update_expense_category(
        self,
        expense_id: str,
        category_id: str,
        confidence: float
    ) -> Dict[str, Any]:
        """Update expense category and confidence"""
        response = (
            self.client.table("expenses")
            .update({
                "category_id": category_id,
                "confidence_score": confidence,
                "updated_at": datetime.utcnow().isoformat()
            })
            .eq("id", expense_id)
            .execute()
        )
        return response.data[0]

    async def get_user_expense_history(
        self,
        user_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get recent expenses for pattern analysis"""
        response = (
            self.client.table("expenses")
            .select("*")
            .eq("user_id", user_id)
            .order("date", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data

    # ============= Category Rules =============

    async def get_category_rules(self) -> List[Dict[str, Any]]:
        """Get all category matching rules"""
        response = self.client.table("category_rules").select("*").execute()
        return response.data

    async def add_category_rule(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new category matching rule"""
        response = self.client.table("category_rules").insert(rule_data).execute()
        return response.data[0]

# Global database instance
db = SupabaseClient()