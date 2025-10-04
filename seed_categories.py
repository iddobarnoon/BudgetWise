"""
Seed Categories - Insert all 20 categories
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

print("🌱 Seeding categories...")

categories = [
    # Essential (9-10)  - Let PostgreSQL generate UUIDs
    {"name": "Housing", "necessity_score": 10, "default_allocation_percent": 30.0, "is_system": True},
    {"name": "Utilities", "necessity_score": 10, "default_allocation_percent": 10.0, "is_system": True},
    {"name": "Groceries", "necessity_score": 9, "default_allocation_percent": 15.0, "is_system": True},
    {"name": "Healthcare", "necessity_score": 9, "default_allocation_percent": 8.0, "is_system": True},
    {"name": "Transportation", "necessity_score": 8, "default_allocation_percent": 10.0, "is_system": True},
    # Important (6-8)
    {"name": "Insurance", "necessity_score": 8, "default_allocation_percent": 5.0, "is_system": True},
    {"name": "Debt Payments", "necessity_score": 8, "default_allocation_percent": 10.0, "is_system": True},
    {"name": "Savings", "necessity_score": 7, "default_allocation_percent": 15.0, "is_system": True},
    {"name": "Childcare", "necessity_score": 7, "default_allocation_percent": 8.0, "is_system": True},
    {"name": "Education", "necessity_score": 6, "default_allocation_percent": 5.0, "is_system": True},
    # Moderate (4-5)
    {"name": "Dining Out", "necessity_score": 4, "default_allocation_percent": 8.0, "is_system": True},
    {"name": "Entertainment", "necessity_score": 3, "default_allocation_percent": 5.0, "is_system": True},
    {"name": "Shopping", "necessity_score": 3, "default_allocation_percent": 7.0, "is_system": True},
    {"name": "Fitness & Wellness", "necessity_score": 5, "default_allocation_percent": 3.0, "is_system": True},
    {"name": "Subscriptions", "necessity_score": 4, "default_allocation_percent": 3.0, "is_system": True},
    # Discretionary (1-3)
    {"name": "Travel", "necessity_score": 2, "default_allocation_percent": 5.0, "is_system": True},
    {"name": "Hobbies", "necessity_score": 2, "default_allocation_percent": 3.0, "is_system": True},
    {"name": "Gifts & Donations", "necessity_score": 3, "default_allocation_percent": 3.0, "is_system": True},
    {"name": "Personal Care", "necessity_score": 4, "default_allocation_percent": 3.0, "is_system": True},
    {"name": "Other", "necessity_score": 1, "default_allocation_percent": 2.0, "is_system": True},
]

try:
    result = supabase.table('categories').insert(categories).execute()
    print(f"✅ Inserted {len(result.data)} categories!")

    for cat in result.data:
        print(f"   - {cat['name']} (score: {cat['necessity_score']})")

except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTrying to insert one by one...")

    inserted = 0
    for cat in categories:
        try:
            supabase.table('categories').insert(cat).execute()
            print(f"   ✓ {cat['name']}")
            inserted += 1
        except Exception as e2:
            print(f"   ✗ {cat['name']}: {e2}")

    print(f"\n✅ Inserted {inserted}/{len(categories)} categories")
