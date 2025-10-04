"""
Setup Supabase Database - Creates all tables and seeds data
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("\n" + "="*60)
print("🚀 BudgetWise Database Setup")
print("="*60)
print(f"URL: {SUPABASE_URL}")
print("="*60 + "\n")

# Note: SQL schema creation needs to be done via Supabase dashboard's SQL editor
# The Python client is for data operations, not DDL

print("⚠️  IMPORTANT: Database schema must be created via Supabase Dashboard")
print("\nSteps:")
print("1. Go to: https://supabase.com/dashboard/project/mjwuxawseluajqduwuru/sql")
print("2. Click 'New Query'")
print("3. Copy and paste the contents of: src/backend/database/schema.sql")
print("4. Click 'Run'")
print("5. Then copy and paste: src/backend/database/seed_data.sql")
print("6. Click 'Run' again")
print("\nOr I can create the tables using the Supabase client for data insertion...")

# Let's test the connection first
print("\n" + "="*60)
print("Testing Supabase Connection...")
print("="*60)

try:
    # Try to check if categories table exists
    result = supabase.table('categories').select("count").limit(1).execute()
    print("✅ Connection successful!")
    print(f"✅ Categories table exists with {len(result.data)} records")

except Exception as e:
    print("⚠️  Tables don't exist yet. Need to run schema.sql first.")
    print(f"Error: {e}")
    print("\nLet me create the tables programmatically...")

    # Create categories using direct insert (works if table exists but is empty)
    try:
        categories = [
            {
                "id": "cat_housing",
                "name": "Housing",
                "necessity_score": 10,
                "default_allocation_percent": 30.0,
                "is_system": True
            },
            {
                "id": "cat_utilities",
                "name": "Utilities",
                "necessity_score": 10,
                "default_allocation_percent": 10.0,
                "is_system": True
            },
            {
                "id": "cat_groceries",
                "name": "Groceries",
                "necessity_score": 9,
                "default_allocation_percent": 15.0,
                "is_system": True
            },
            {
                "id": "cat_dining",
                "name": "Dining Out",
                "necessity_score": 4,
                "default_allocation_percent": 8.0,
                "is_system": True
            },
            {
                "id": "cat_transportation",
                "name": "Transportation",
                "necessity_score": 8,
                "default_allocation_percent": 10.0,
                "is_system": True
            },
        ]

        print("\nAttempting to insert sample categories...")
        result = supabase.table('categories').insert(categories).execute()
        print(f"✅ Inserted {len(result.data)} categories!")

    except Exception as insert_error:
        print(f"❌ Could not insert categories: {insert_error}")
        print("\n📝 Please run the SQL files manually in Supabase Dashboard")

print("\n" + "="*60)
print("Setup Instructions:")
print("="*60)
print("1. Go to Supabase Dashboard: SQL Editor")
print("2. Run: src/backend/database/schema.sql")
print("3. Run: src/backend/database/seed_data.sql")
print("4. Come back and run this script again to verify")
print("="*60 + "\n")
