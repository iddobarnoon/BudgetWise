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
# Each rule has: category_id, merchant_patterns (array), keywords (array), priority
CATEGORY_RULES = [
    # Groceries
    {"category_name": "Groceries", "merchant_patterns": ["walmart"], "keywords": ["grocery", "food"], "priority": 10},
    {"category_name": "Groceries", "merchant_patterns": ["target"], "keywords": ["grocery"], "priority": 10},
    {"category_name": "Groceries", "merchant_patterns": ["kroger"], "keywords": ["grocery"], "priority": 10},
    {"category_name": "Groceries", "merchant_patterns": ["safeway"], "keywords": ["grocery"], "priority": 10},
    {"category_name": "Groceries", "merchant_patterns": ["whole foods"], "keywords": ["grocery", "organic"], "priority": 10},
    {"category_name": "Groceries", "merchant_patterns": ["trader joes", "trader joe"], "keywords": ["grocery"], "priority": 10},
    {"category_name": "Groceries", "merchant_patterns": ["costco"], "keywords": ["grocery", "wholesale"], "priority": 10},
    {"category_name": "Groceries", "merchant_patterns": ["sams club", "sam's club"], "keywords": ["grocery", "wholesale"], "priority": 10},
    {"category_name": "Groceries", "merchant_patterns": ["aldi"], "keywords": ["grocery"], "priority": 10},
    {"category_name": "Groceries", "merchant_patterns": ["publix"], "keywords": ["grocery"], "priority": 10},

    # Transportation/Gas
    {"category_name": "Transportation", "merchant_patterns": ["shell"], "keywords": ["gas", "fuel"], "priority": 10},
    {"category_name": "Transportation", "merchant_patterns": ["chevron"], "keywords": ["gas", "fuel"], "priority": 10},
    {"category_name": "Transportation", "merchant_patterns": ["exxon"], "keywords": ["gas", "fuel"], "priority": 10},
    {"category_name": "Transportation", "merchant_patterns": ["bp"], "keywords": ["gas", "fuel"], "priority": 10},
    {"category_name": "Transportation", "merchant_patterns": ["gas station"], "keywords": ["gas", "fuel"], "priority": 8},
    {"category_name": "Transportation", "merchant_patterns": ["fuel"], "keywords": ["gas"], "priority": 8},
    {"category_name": "Transportation", "merchant_patterns": ["uber"], "keywords": ["ride", "transport"], "priority": 10},
    {"category_name": "Transportation", "merchant_patterns": ["lyft"], "keywords": ["ride", "transport"], "priority": 10},
    {"category_name": "Transportation", "merchant_patterns": ["taxi", "cab"], "keywords": ["ride", "transport"], "priority": 10},

    # Dining/Restaurants
    {"category_name": "Dining Out", "merchant_patterns": ["restaurant"], "keywords": ["dining", "food"], "priority": 10},
    {"category_name": "Dining Out", "merchant_patterns": ["mcdonalds", "mcdonald"], "keywords": ["fast food"], "priority": 10},
    {"category_name": "Dining Out", "merchant_patterns": ["burger king"], "keywords": ["fast food"], "priority": 10},
    {"category_name": "Dining Out", "merchant_patterns": ["starbucks"], "keywords": ["coffee", "cafe"], "priority": 10},
    {"category_name": "Dining Out", "merchant_patterns": ["subway"], "keywords": ["fast food", "sandwich"], "priority": 10},
    {"category_name": "Dining Out", "merchant_patterns": ["chipotle"], "keywords": ["fast food", "mexican"], "priority": 10},
    {"category_name": "Dining Out", "merchant_patterns": ["pizza"], "keywords": ["food"], "priority": 8},
    {"category_name": "Dining Out", "merchant_patterns": ["cafe", "coffee shop"], "keywords": ["coffee"], "priority": 8},
    {"category_name": "Dining Out", "merchant_patterns": ["doordash"], "keywords": ["delivery", "food"], "priority": 10},
    {"category_name": "Dining Out", "merchant_patterns": ["grubhub"], "keywords": ["delivery", "food"], "priority": 10},
    {"category_name": "Dining Out", "merchant_patterns": ["uber eats"], "keywords": ["delivery", "food"], "priority": 10},

    # Entertainment
    {"category_name": "Entertainment", "merchant_patterns": ["netflix"], "keywords": ["streaming", "video"], "priority": 10},
    {"category_name": "Entertainment", "merchant_patterns": ["spotify"], "keywords": ["streaming", "music"], "priority": 10},
    {"category_name": "Entertainment", "merchant_patterns": ["hulu"], "keywords": ["streaming", "video"], "priority": 10},
    {"category_name": "Entertainment", "merchant_patterns": ["disney", "disney+"], "keywords": ["streaming", "video"], "priority": 10},
    {"category_name": "Entertainment", "merchant_patterns": ["movie"], "keywords": ["cinema", "film"], "priority": 9},
    {"category_name": "Entertainment", "merchant_patterns": ["theater", "theatre"], "keywords": ["cinema", "movie"], "priority": 9},
    {"category_name": "Entertainment", "merchant_patterns": ["cinema"], "keywords": ["movie"], "priority": 9},
    {"category_name": "Entertainment", "merchant_patterns": ["amc"], "keywords": ["movie", "cinema"], "priority": 10},
    {"category_name": "Entertainment", "merchant_patterns": ["steam"], "keywords": ["gaming", "games"], "priority": 10},
    {"category_name": "Entertainment", "merchant_patterns": ["playstation", "psn"], "keywords": ["gaming", "games"], "priority": 10},
    {"category_name": "Entertainment", "merchant_patterns": ["xbox"], "keywords": ["gaming", "games"], "priority": 10},

    # Utilities
    {"category_name": "Utilities", "merchant_patterns": ["electric", "electricity"], "keywords": ["utility", "power"], "priority": 10},
    {"category_name": "Utilities", "merchant_patterns": ["water"], "keywords": ["utility"], "priority": 10},
    {"category_name": "Utilities", "merchant_patterns": ["internet"], "keywords": ["utility", "isp"], "priority": 10},
    {"category_name": "Utilities", "merchant_patterns": ["comcast", "xfinity"], "keywords": ["internet", "cable"], "priority": 10},
    {"category_name": "Utilities", "merchant_patterns": ["verizon"], "keywords": ["phone", "internet"], "priority": 10},
    {"category_name": "Utilities", "merchant_patterns": ["att", "at&t"], "keywords": ["phone", "internet"], "priority": 10},
    {"category_name": "Utilities", "merchant_patterns": ["tmobile", "t-mobile"], "keywords": ["phone", "mobile"], "priority": 10},

    # Shopping
    {"category_name": "Shopping", "merchant_patterns": ["amazon"], "keywords": ["online", "retail"], "priority": 10},
    {"category_name": "Shopping", "merchant_patterns": ["ebay"], "keywords": ["online", "auction"], "priority": 10},
    {"category_name": "Shopping", "merchant_patterns": ["etsy"], "keywords": ["online", "handmade"], "priority": 10},
    {"category_name": "Shopping", "merchant_patterns": ["bestbuy", "best buy"], "keywords": ["electronics", "retail"], "priority": 10},
    {"category_name": "Shopping", "merchant_patterns": ["macys", "macy"], "keywords": ["retail", "clothing"], "priority": 10},
    {"category_name": "Shopping", "merchant_patterns": ["nordstrom"], "keywords": ["retail", "clothing"], "priority": 10},

    # Healthcare
    {"category_name": "Healthcare", "merchant_patterns": ["pharmacy"], "keywords": ["medical", "medication"], "priority": 10},
    {"category_name": "Healthcare", "merchant_patterns": ["cvs"], "keywords": ["pharmacy", "medical"], "priority": 10},
    {"category_name": "Healthcare", "merchant_patterns": ["walgreens"], "keywords": ["pharmacy", "medical"], "priority": 10},
    {"category_name": "Healthcare", "merchant_patterns": ["doctor", "dr"], "keywords": ["medical", "health"], "priority": 9},
    {"category_name": "Healthcare", "merchant_patterns": ["hospital"], "keywords": ["medical", "health"], "priority": 9},
    {"category_name": "Healthcare", "merchant_patterns": ["medical"], "keywords": ["health"], "priority": 9},
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
            'merchant_patterns': rule['merchant_patterns'],
            'keywords': rule['keywords'],
            'priority': rule['priority']
        }

        try:
            supabase.table('category_rules').insert(rule_data).execute()
            inserted_count += 1
            print(f"  ✓ Added rule: {category_name} <- {rule['merchant_patterns']}")
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
<<<<<<< HEAD
            print(f"  - {cat_name}: {rule['merchant_patterns']} (priority: {rule['priority']})")
=======
            patterns = ', '.join(rule.get('merchant_patterns', []))
            print(f"  - {cat_name}: {patterns} (priority: {rule.get('priority', 0)})")
>>>>>>> 956236fe0a03ce153a4af285ed7ee1f32703413f

if __name__ == "__main__":
    print("="*60)
    print("CATEGORY RULES SEEDING SCRIPT")
    print("="*60)
    seed_category_rules()
