from supabase import create_client, Client
from typing import Optional, List, Dict, Any
import os
from datetime import datetime
from decimal import Decimal

class SupabaseClient:
    """Wrapper for Supabase database operations"""

    def __init__(self):
        url = "https://mjwuxawseluajqduwuru.supabase.co"
        key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1qd3V4YXdzZWx1YWpxZHV3dXJ1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk1OTI1NjAsImV4cCI6MjA3NTE2ODU2MH0.mrk7QZzso29zihyJ6oIjyxiigJGcapK2k4Vyy7cLhZ8"
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
        self.client: Client = create_client(url, key)

    # ============= Categories =============

    def get_categories(self, include_custom: bool = False) -> List[Dict[str, Any]]:
        """Get all system categories, optionally including custom ones"""
        query = self.client.table("categories").select("*")
        if not include_custom:
            query = query.eq("is_system", True)
        response = query.execute()
        return response.data

    def get_category_by_id(self, category_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific category by ID"""
        response = self.client.table("categories").select("*").eq("id", category_id).execute()
        return response.data[0] if response.data else None

    def get_category_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a category by name (case-insensitive)"""
        response = self.client.table("categories").select("*").ilike("name", name).execute()
        return response.data[0] if response.data else None

    # ============= User Category Preferences =============

    def get_user_category_preferences(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all category preferences for a user"""
        response = self.client.table("user_category_preferences").select("*").eq("user_id", user_id).execute()
        return response.data

    def get_user_override(self, user_id: str, merchant: str) -> Optional[str]:
        """Get user's preferred category for a specific merchant"""
        response = (
            self.client.table("user_merchant_overrides")
            .select("category_id")
            .eq("user_id", user_id)
            .eq("merchant", merchant)
            .execute()
        )
        return response.data[0]["category_id"] if response.data else None

    def save_user_override(self, user_id: str, merchant: str, category_id: str) -> None:
        """Save user's category preference for a merchant"""
        self.client.table("user_merchant_overrides").upsert({
            "user_id": user_id,
            "merchant": merchant,
            "category_id": category_id,
            "updated_at": datetime.utcnow().isoformat()
        }).execute()

    def update_user_category_priority(
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

    def save_expense(self, expense_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save an expense to the database"""
        response = self.client.table("expenses").insert(expense_data).execute()
        return response.data[0]

    def update_expense_category(
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
                "updated_at": datetime.now().isoformat()
            })
            .eq("id", expense_id)
            .execute()
        )
        return response.data[0]

    def get_user_expense_history(
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

    def get_category_rules(self) -> List[Dict[str, Any]]:
        """Get all category matching rules"""
        response = self.client.table("category_rules").select("*").execute()
        return response.data

    def add_category_rule(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new category matching rule"""
        response = self.client.table("category_rules").insert(rule_data).execute()
        return response.data[0]

    # ============= Users =============

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile by ID"""
        try:
            response = self.client.table("users").select("*").eq("id", user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error fetching user {user_id}: {e}")
            return None

    # ============= Chat Messages =============

    def save_chat_message(
        self,
        user_id: str,
        role: str,
        content: str,
        conversation_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Save a chat message to the database"""
        message_data = {
            "user_id": user_id,
            "role": role,
            "content": content,
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat(),
        }
        if metadata:
            message_data["metadata"] = metadata

        response = self.client.table("chat_messages").insert(message_data).execute()
        return response.data[0] if response.data else {}

    def get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get chat history for a conversation"""
        try:
            response = (
                self.client.table("chat_messages")
                .select("*")
                .eq("conversation_id", conversation_id)
                .order("timestamp", desc=False)  # Chronological order
                .limit(limit)
                .execute()
            )
            return response.data
        except Exception as e:
            print(f"Error fetching conversation history: {e}")
            return []

# Global database instance
db = SupabaseClient()