"""
Initialize Database with SQLAlchemy
Creates all tables and seeds initial data
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "src" / "backend"))

from shared.db_session import init_db, get_db_context, engine
from shared.db_models import Category, CategoryRule
from sqlalchemy import text

print("\n" + "="*60)
print("🚀 BudgetWise Database Initialization")
print("="*60)

# Test connection first
print("\n1. Testing database connection...")
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.scalar()
        print(f"✅ Connected to PostgreSQL!")
        print(f"   Version: {version[:50]}...")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\n⚠️  Please update DATABASE_URL in .env file")
    print("   Format: postgresql://postgres:PASSWORD@db.PROJECT_ID.supabase.co:5432/postgres")
    sys.exit(1)

# Create tables
print("\n2. Creating database tables...")
try:
    init_db()
except Exception as e:
    print(f"⚠️  Error creating tables: {e}")
    print("   (Tables may already exist - this is OK)")

# Seed categories
print("\n3. Seeding category data...")
try:
    with get_db_context() as db:
        # Check if categories already exist
        existing_count = db.query(Category).count()

        if existing_count > 0:
            print(f"   Categories already exist ({existing_count} found)")
        else:
            # Seed categories
            categories = [
                # Essential (9-10)
                Category(id="cat_housing", name="Housing", necessity_score=10, default_allocation_percent=30.0),
                Category(id="cat_utilities", name="Utilities", necessity_score=10, default_allocation_percent=10.0),
                Category(id="cat_groceries", name="Groceries", necessity_score=9, default_allocation_percent=15.0),
                Category(id="cat_healthcare", name="Healthcare", necessity_score=9, default_allocation_percent=8.0),
                Category(id="cat_transportation", name="Transportation", necessity_score=8, default_allocation_percent=10.0),

                # Important (6-8)
                Category(id="cat_insurance", name="Insurance", necessity_score=8, default_allocation_percent=5.0),
                Category(id="cat_debt_payments", name="Debt Payments", necessity_score=8, default_allocation_percent=10.0),
                Category(id="cat_savings", name="Savings", necessity_score=7, default_allocation_percent=15.0),
                Category(id="cat_childcare", name="Childcare", necessity_score=7, default_allocation_percent=8.0),
                Category(id="cat_education", name="Education", necessity_score=6, default_allocation_percent=5.0),

                # Moderate (4-5)
                Category(id="cat_dining", name="Dining Out", necessity_score=4, default_allocation_percent=8.0),
                Category(id="cat_entertainment", name="Entertainment", necessity_score=3, default_allocation_percent=5.0),
                Category(id="cat_shopping", name="Shopping", necessity_score=3, default_allocation_percent=7.0),
                Category(id="cat_fitness", name="Fitness & Wellness", necessity_score=5, default_allocation_percent=3.0),
                Category(id="cat_subscriptions", name="Subscriptions", necessity_score=4, default_allocation_percent=3.0),

                # Discretionary (1-3)
                Category(id="cat_travel", name="Travel", necessity_score=2, default_allocation_percent=5.0),
                Category(id="cat_hobbies", name="Hobbies", necessity_score=2, default_allocation_percent=3.0),
                Category(id="cat_gifts", name="Gifts & Donations", necessity_score=3, default_allocation_percent=3.0),
                Category(id="cat_personal_care", name="Personal Care", necessity_score=4, default_allocation_percent=3.0),
                Category(id="cat_other", name="Other", necessity_score=1, default_allocation_percent=2.0),
            ]

            db.add_all(categories)
            db.commit()
            print(f"✅ Inserted {len(categories)} categories!")

            # Seed category rules
            rules = [
                # Groceries
                CategoryRule(
                    category_id="cat_groceries",
                    keywords=["grocery", "supermarket", "market", "food", "produce"],
                    merchant_patterns=["whole foods", "trader joes", "safeway", "kroger", "walmart", "target"],
                    match_type="substring",
                    priority=9
                ),
                # Dining
                CategoryRule(
                    category_id="cat_dining",
                    keywords=["restaurant", "cafe", "coffee", "diner", "pizza", "burger"],
                    merchant_patterns=["starbucks", "mcdonalds", "chipotle", "subway", "panera"],
                    match_type="substring",
                    priority=7
                ),
                # Transportation
                CategoryRule(
                    category_id="cat_transportation",
                    keywords=["gas", "fuel", "uber", "lyft", "taxi", "parking"],
                    merchant_patterns=["shell", "chevron", "uber", "lyft"],
                    match_type="substring",
                    priority=8
                ),
            ]

            db.add_all(rules)
            db.commit()
            print(f"✅ Inserted {len(rules)} category rules!")

except Exception as e:
    print(f"❌ Error seeding data: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("✅ Database initialization complete!")
print("="*60)
print("\nNext steps:")
print("1. Start the Budget Engine: cd src/backend/components/budget-engine && python3 app.py")
print("2. Start the Ranking System: cd src/backend/components/ranking-system && python3 app.py")
print("="*60 + "\n")
