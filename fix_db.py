"""
Fix the users table to allow direct inserts without auth.users constraint
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# First, try to insert the test user directly
user_id = "db8f4c2a-3e5f-4d9b-8a6c-1f7e9d2b4a8c"

user_data = {
    "id": user_id,
    "email": "test@budgetwise.com",
    "full_name": "Test User",
    "monthly_income": 10000.00,
    "financial_goals": ["Save for emergency fund"],
    "risk_tolerance": "moderate"
}

try:
    # Try direct insert
    result = supabase.table('users').insert(user_data).execute()
    print(f"✅ Test user created successfully!")
    print(f"   ID: {user_id}")
    print(f"   Email: test@budgetwise.com")
except Exception as e:
    error_msg = str(e)
    if "violates foreign key constraint" in error_msg:
        print("❌ Foreign key constraint blocking insert")
        print("\n⚠️  You need to run this SQL in Supabase SQL Editor:")
        print("\n" + "="*60)
        print("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_id_fkey;")
        print("="*60)
        print("\nThen run this script again.")
    elif "duplicate key" in error_msg:
        print(f"✅ Test user already exists: {user_id}")
    else:
        print(f"❌ Error: {e}")
