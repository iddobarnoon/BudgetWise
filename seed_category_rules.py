"""
Seed category_rules table with matching patterns for expense categorization
"""

import os
from supabase import create_client
from dotenv import load_dotenv, find_dotenv

# Load .env from project root
load_dotenv(find_dotenv())

# Initialize Supabase
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Category rules data structure
# Each rule has: category_id, merchant_pattern (main match), keywords (additional matches), weight (priority)
CATEGORY_RULES = [
    # Groceries
    {"category_name": "Groceries", "merchant_pattern": "walmart", "weight": 10},
    {"category_name": "Groceries", "merchant_pattern": "target", "weight": 10},
    {"category_name": "Groceries", "merchant_pattern": "kroger", "weight": 10},
    {"category_name": "Groceries", "merchant_pattern": "safeway", "weight": 10},
    {"category_name": "Groceries", "merchant_pattern": "whole foods", "weight": 10},
    {"category_name": "Groceries", "merchant_pattern": "trader joes", "weight": 10},
    {"category_name": "Groceries", "merchant_pattern": "costco", "weight": 10},
    {"category_name": "Groceries", "merchant_pattern": "sams club", "weight": 10},
    {"category_name": "Groceries", "merchant_pattern": "aldi", "weight": 10},
    {"category_name": "Groceries", "merchant_pattern": "publix", "weight": 10},

    # Transportation/Gas
    {"category_name": "Transportation", "merchant_pattern": "shell", "weight": 10},
    {"category_name": "Transportation", "merchant_pattern": "chevron", "weight": 10},
    {"category_name": "Transportation", "merchant_pattern": "exxon", "weight": 10},
    {"category_name": "Transportation", "merchant_pattern": "bp", "weight": 10},
    {"category_name": "Transportation", "merchant_pattern": "gas", "weight": 8},
    {"category_name": "Transportation", "merchant_pattern": "fuel", "weight": 8},
    {"category_name": "Transportation", "merchant_pattern": "uber", "weight": 10},
    {"category_name": "Transportation", "merchant_pattern": "lyft", "weight": 10},
    {"category_name": "Transportation", "merchant_pattern": "taxi", "weight": 10},

    # Dining/Restaurants
    {"category_name": "Dining Out", "merchant_pattern": "restaurant", "weight": 10},
    {"category_name": "Dining Out", "merchant_pattern": "mcdonalds", "weight": 10},
    {"category_name": "Dining Out", "merchant_pattern": "burger king", "weight": 10},
    {"category_name": "Dining Out", "merchant_pattern": "starbucks", "weight": 10},
    {"category_name": "Dining Out", "merchant_pattern": "subway", "weight": 10},
    {"category_name": "Dining Out", "merchant_pattern": "chipotle", "weight": 10},
    {"category_name": "Dining Out", "merchant_pattern": "pizza", "weight": 8},
    {"category_name": "Dining Out", "merchant_pattern": "cafe", "weight": 8},
    {"category_name": "Dining Out", "merchant_pattern": "coffee", "weight": 7},
    {"category_name": "Dining Out", "merchant_pattern": "doordash", "weight": 10},
    {"category_name": "Dining Out", "merchant_pattern": "grubhub", "weight": 10},
    {"category_name": "Dining Out", "merchant_pattern": "uber eats", "weight": 10},

    # Entertainment
    {"category_name": "Entertainment", "merchant_pattern": "netflix", "weight": 10},
    {"category_name": "Entertainment", "merchant_pattern": "spotify", "weight": 10},
    {"category_name": "Entertainment", "merchant_pattern": "hulu", "weight": 10},
    {"category_name": "Entertainment", "merchant_pattern": "disney", "weight": 10},
    {"category_name": "Entertainment", "merchant_pattern": "movie", "weight": 9},
    {"category_name": "Entertainment", "merchant_pattern": "theater", "weight": 9},
    {"category_name": "Entertainment", "merchant_pattern": "cinema", "weight": 9},
    {"category_name": "Entertainment", "merchant_pattern": "amc", "weight": 10},
    {"category_name": "Entertainment", "merchant_pattern": "steam", "weight": 10},
    {"category_name": "Entertainment", "merchant_pattern": "playstation", "weight": 10},
    {"category_name": "Entertainment", "merchant_pattern": "xbox", "weight": 10},

    # Utilities
    {"category_name": "Utilities", "merchant_pattern": "electric", "weight": 10},
    {"category_name": "Utilities", "merchant_pattern": "water", "weight": 10},
    {"category_name": "Utilities", "merchant_pattern": "internet", "weight": 10},
    {"category_name": "Utilities", "merchant_pattern": "comcast", "weight": 10},
    {"category_name": "Utilities", "merchant_pattern": "verizon", "weight": 10},
    {"category_name": "Utilities", "merchant_pattern": "att", "weight": 10},
    {"category_name": "Utilities", "merchant_pattern": "tmobile", "weight": 10},

    # Shopping
    {"category_name": "Shopping", "merchant_pattern": "amazon", "weight": 10},
    {"category_name": "Shopping", "merchant_pattern": "ebay", "weight": 10},
    {"category_name": "Shopping", "merchant_pattern": "etsy", "weight": 10},
    {"category_name": "Shopping", "merchant_pattern": "bestbuy", "weight": 10},
    {"category_name": "Shopping", "merchant_pattern": "macys", "weight": 10},
    {"category_name": "Shopping", "merchant_pattern": "nordstrom", "weight": 10},

    # Healthcare
    {"category_name": "Healthcare", "merchant_pattern": "pharmacy", "weight": 10},
    {"category_name": "Healthcare", "merchant_pattern": "cvs", "weight": 10},
    {"category_name": "Healthcare", "merchant_pattern": "walgreens", "weight": 10},
    {"category_name": "Healthcare", "merchant_pattern": "doctor", "weight": 9},
    {"category_name": "Healthcare", "merchant_pattern": "hospital", "weight": 9},
    {"category_name": "Healthcare", "merchant_pattern": "medical", "weight": 9},
]

def seed_category_rules():
    """Seed the category_rules table with predefined patterns"""

    print("Fetching categories...")
    # Get all categories
    categories_result = supabase.table('categories').select('id, name').execute()
    categories = {cat['name']: cat['id'] for cat in categories_result.data}

    print(f"Found {len(categories)} categories: {list(categories.keys())}")

    # Clear existing rules
    print("\nClearing existing rules...")
    try:
        supabase.table('category_rules').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
        print("Existing rules cleared")
    except Exception as e:
        print(f"Note: {e}")

    # Insert new rules
    print("\nInserting new rules...")
    inserted_count = 0
    skipped_count = 0

    for rule in CATEGORY_RULES:
        category_name = rule['category_name']

        if category_name not in categories:
            print(f"  ⚠️  Skipping rule for '{category_name}' - category not found")
            skipped_count += 1
            continue

        rule_data = {
            'category_id': categories[category_name],
            'merchant_patterns': [rule['merchant_pattern']],  # Array field
            'priority': rule['weight']  # Changed from 'weight' to 'priority'
        }

        try:
            supabase.table('category_rules').insert(rule_data).execute()
            inserted_count += 1
            print(f"  ✓ Added rule: {category_name} <- '{rule['merchant_pattern']}'")
        except Exception as e:
            print(f"  ✗ Error adding rule for {category_name}: {e}")

    print(f"\n{'='*60}")
    print(f"Seeding complete!")
    print(f"  Inserted: {inserted_count} rules")
    print(f"  Skipped:  {skipped_count} rules")
    print(f"{'='*60}")

    # Verify
    print("\nVerifying...")
    result = supabase.table('category_rules').select('*').execute()
    print(f"Total rules in database: {len(result.data)}")

    # Show sample rules
    if result.data:
        print("\nSample rules:")
        for rule in result.data[:5]:
            cat_name = next((name for name, id in categories.items() if id == rule['category_id']), 'Unknown')
            patterns = ', '.join(rule.get('merchant_patterns', []))
            print(f"  - {cat_name}: {patterns} (priority: {rule.get('priority', 0)})")

if __name__ == "__main__":
    print("="*60)
    print("CATEGORY RULES SEEDING SCRIPT")
    print("="*60)
    seed_category_rules()
