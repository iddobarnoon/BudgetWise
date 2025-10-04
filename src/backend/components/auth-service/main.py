"""
Auth Service - User authentication and session management
Uses Supabase Auth for JWT token generation and validation
"""

import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class AuthService:
    """Handles user authentication with Supabase"""

    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )

    async def register_user(
        self,
        email: str,
        password: str,
        full_name: str,
        monthly_income: float = 0.0
    ) -> dict:
        """
        Register new user with Supabase Auth
        Returns: User object with auth data
        """
        try:
            # Create auth user
            auth_response = self.supabase.auth.sign_up({
                "email": email,
                "password": password
            })

            if auth_response.user:
                user_id = auth_response.user.id

                # Create user profile in users table
                user_data = {
                    "id": user_id,
                    "email": email,
                    "full_name": full_name,
                    "monthly_income": monthly_income,
                    "financial_goals": [],
                    "risk_tolerance": "moderate"
                }

                self.supabase.table('users').insert(user_data).execute()

                return {
                    "success": True,
                    "user_id": user_id,
                    "email": email,
                    "access_token": auth_response.session.access_token if auth_response.session else None,
                    "refresh_token": auth_response.session.refresh_token if auth_response.session else None
                }

            return {"success": False, "error": "Failed to create user"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def login(self, email: str, password: str) -> dict:
        """
        Authenticate user and create session
        Returns: Session with JWT tokens
        """
        try:
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if auth_response.user and auth_response.session:
                return {
                    "success": True,
                    "user_id": auth_response.user.id,
                    "email": auth_response.user.email,
                    "access_token": auth_response.session.access_token,
                    "refresh_token": auth_response.session.refresh_token,
                    "expires_at": auth_response.session.expires_at
                }

            return {"success": False, "error": "Invalid credentials"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def validate_token(self, token: str) -> dict:
        """
        Validate JWT and return user context
        """
        try:
            user_response = self.supabase.auth.get_user(token)

            if user_response.user:
                # Get user profile from database
                user_profile = self.supabase.table('users').select('*').eq('id', user_response.user.id).execute()

                return {
                    "valid": True,
                    "user_id": user_response.user.id,
                    "email": user_response.user.email,
                    "profile": user_profile.data[0] if user_profile.data else None
                }

            return {"valid": False, "error": "Invalid token"}

        except Exception as e:
            return {"valid": False, "error": str(e)}

    async def logout(self, token: str) -> dict:
        """Sign out user and invalidate session"""
        try:
            self.supabase.auth.sign_out()
            return {"success": True, "message": "Logged out successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def refresh_session(self, refresh_token: str) -> dict:
        """Refresh access token using refresh token"""
        try:
            auth_response = self.supabase.auth.refresh_session(refresh_token)

            if auth_response.session:
                return {
                    "success": True,
                    "access_token": auth_response.session.access_token,
                    "refresh_token": auth_response.session.refresh_token,
                    "expires_at": auth_response.session.expires_at
                }

            return {"success": False, "error": "Failed to refresh session"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_user_profile(self, user_id: str) -> Optional[dict]:
        """Get user profile from database"""
        try:
            result = self.supabase.table('users').select('*').eq('id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error fetching user profile: {e}")
            return None

# Global auth service instance
auth_service = AuthService()
