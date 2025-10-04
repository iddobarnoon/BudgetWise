"""
Initialize Database using Supabase Client
Creates tables and seeds data using Supabase REST API
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
print("🚀 BudgetWise Database Setup (Supabase Client)")
print("="*60)
print(f"URL: {SUPABASE_URL}")
print("="*60 + "\n")

# Test connection
print("1. Testing connection...")
try:
    # Try to query categories table
    result = supabase.table('categories').select("*").limit(1).execute()
    print(f"✅ Connection successful!")

    if len(result.data) > 0:
        print(f"✅ Categories table exists with {len(result.data)} records")
        print("\n⚠️  Tables already exist. Skipping creation.")
        print("\nTo reset database:")
        print("1. Go to: https://supabase.com/dashboard/project/mjwuxawseluajqduwuru/editor")
        print("2. Delete all tables manually")
        print("3. Run this script again")
    else:
        print("📊 Categories table exists but is empty. Seeding data...")

except Exception as e:
    print(f"⚠️  Tables don't exist yet: {e}")
    print("\n📝 You need to create tables first using SQL Editor:")
    print("\n" + "="*60)
    print("STEP-BY-STEP INSTRUCTIONS:")
    print("="*60)
    print("\n1. Go to SQL Editor:")
    print("   https://supabase.com/dashboard/project/mjwuxawseluajqduwuru/sql/new")
    print("\n2. Copy the ENTIRE contents of this file:")
    print("   src/backend/database/schema.sql")
    print("\n3. Paste into SQL Editor")
    print("\n4. Click 'RUN' button (green play button)")
    print("\n5. Wait for success message")
    print("\n6. Then run this script again: python3 init_database_supabase.py")
    print("="*60 + "\n")
    exit(1)

# Seed categories if table is empty
print("\n2. Seeding categories...")
try:
    # Check if categories exist
    result = supabase.table('categories').select("count").execute()

    if len(result.data) > 0:
        print(f"   Categories already exist ({len(result.data)} found)")
    else:
        # Seed categories
        categories = [
            # Essential (9-10)
            {"id": "cat_housing", "name": "Housing", "necessity_score": 10, "default_allocation_percent": 30.0, "is_system": True},
            {"id": "cat_utilities", "name": "Utilities", "necessity_score": 10, "default_allocation_percent": 10.0, "is_system": True},
            {"id": "cat_groceries", "name": "Groceries", "necessity_score": 9, "default_allocation_percent": 15.0, "is_system": True},
            {"id": "cat_healthcare", "name": "Healthcare", "necessity_score": 9, "default_allocation_percent": 8.0, "is_system": True},
            {"id": "cat_transportation", "name": "Transportation", "necessity_score": 8, "default_allocation_percent": 10.0, "is_system": True},
            # Important (6-8)
            {"id": "cat_insurance", "name": "Insurance", "necessity_score": 8, "default_allocation_percent": 5.0, "is_system": True},
            {"id": "cat_debt_payments", "name": "Debt Payments", "necessity_score": 8, "default_allocation_percent": 10.0, "is_system": True},
            {"id": "cat_savings", "name": "Savings", "necessity_score": 7, "default_allocation_percent": 15.0, "is_system": True},
            {"id": "cat_childcare", "name": "Childcare", "necessity_score": 7, "default_allocation_percent": 8.0, "is_system": True},
            {"id": "cat_education", "name": "Education", "necessity_score": 6, "default_allocation_percent": 5.0, "is_system": True},
            # Moderate (4-5)
            {"id": "cat_dining", "name": "Dining Out", "necessity_score": 4, "default_allocation_percent": 8.0, "is_system": True},
            {"id": "cat_entertainment", "name": "Entertainment", "necessity_score": 3, "default_allocation_percent": 5.0, "is_system": True},
            {"id": "cat_shopping", "name": "Shopping", "necessity_score": 3, "default_allocation_percent": 7.0, "is_system": True},
            {"id": "cat_fitness", "name": "Fitness & Wellness", "necessity_score": 5, "default_allocation_percent": 3.0, "is_system": True},
            {"id": "cat_subscriptions", "name": "Subscriptions", "necessity_score": 4, "default_allocation_percent": 3.0, "is_system": True},
            # Discretionary (1-3)
            {"id": "cat_travel", "name": "Travel", "necessity_score": 2, "default_allocation_percent": 5.0, "is_system": True},
            {"id": "cat_hobbies", "name": "Hobbies", "necessity_score": 2, "default_allocation_percent": 3.0, "is_system": True},
            {"id": "cat_gifts", "name": "Gifts & Donations", "necessity_score": 3, "default_allocation_percent": 3.0, "is_system": True},
            {"id": "cat_personal_care", "name": "Personal Care", "necessity_score": 4, "default_allocation_percent": 3.0, "is_system": True},
            {"id": "cat_other", "name": "Other", "necessity_score": 1, "default_allocation_percent": 2.0, "is_system": True},
        ]

        result = supabase.table('categories').insert(categories).execute()
        print(f"✅ Inserted {len(result.data)} categories!")

        # Seed category rules
        print("\n3. Seeding category rules...")
        rules = [
            {
                "category_id": "cat_groceries",
                "keywords": ["grocery", "supermarket", "market", "food", "produce"],
                "merchant_patterns": ["whole foods", "trader joes", "safeway", "kroger"],
                "match_type": "substring",
                "priority": 9
            },
            {
                "category_id": "cat_dining",
                "keywords": ["restaurant", "cafe", "coffee", "diner"],
                "merchant_patterns": ["starbucks", "mcdonalds", "chipotle"],
                "match_type": "substring",
                "priority": 7
            },
            {
                "category_id": "cat_transportation",
                "keywords": ["gas", "fuel", "uber", "lyft"],
                "merchant_patterns": ["shell", "chevron", "uber"],
                "match_type": "substring",
                "priority": 8
            },
        ]

        result = supabase.table('category_rules').insert(rules).execute()
        print(f"✅ Inserted {len(result.data)} category rules!")

except Exception as e:
    print(f"❌ Error seeding data: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("✅ Database setup complete!")
print("="*60)
print("\nNext steps:")
print("1. Test by querying categories:")
print("   python3 -c \"from supabase import create_client; import os; from dotenv import load_dotenv; load_dotenv(); s = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY')); print(len(s.table('categories').select('*').execute().data), 'categories')\"")
print("\n2. Start services with Supabase connection")
print("="*60 + "\n")
