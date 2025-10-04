"""
Create a test user in the database
"""

import os
from supabase import create_client
from dotenv import load_dotenv
import uuid

load_dotenv()

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Create a test user
user_id = "db8f4c2a-3e5f-4d9b-8a6c-1f7e9d2b4a8c"

user_data = {
    "id": user_id,
    "email": "test@budgetwise.com",
    "full_name": "Test User",
    "monthly_income": 10000.00,
    "financial_goals": ["Save for emergency fund", "Pay off debt"],
    "risk_tolerance": "moderate"
}

try:
    result = supabase.table('users').insert(user_data).execute()
    print(f"✅ Test user created!")
    print(f"   ID: {user_id}")
    print(f"   Email: test@budgetwise.com")
    print(f"\nYou can now use this user_id in the API:")
    print(f'   "user_id": "{user_id}"')
except Exception as e:
    if "duplicate key" in str(e):
        print(f"✅ Test user already exists: {user_id}")
        print(f"\nYou can use this user_id in the API:")
        print(f'   "user_id": "{user_id}"')
    else:
        print(f"❌ Error: {e}")
