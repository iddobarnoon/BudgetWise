-- Seed Data for BudgetWise Categories and Rules

-- ============= System Categories =============
-- Ordered by necessity_score (10 = most essential, 1 = luxury)

INSERT INTO categories (id, name, necessity_score, default_allocation_percent, is_system) VALUES
    -- Essential (9-10)
    ('cat_housing', 'Housing', 10, 30.0, true),
    ('cat_utilities', 'Utilities', 10, 10.0, true),
    ('cat_groceries', 'Groceries', 9, 15.0, true),
    ('cat_healthcare', 'Healthcare', 9, 8.0, true),
    ('cat_transportation', 'Transportation', 8, 10.0, true),

    -- Important (6-8)
    ('cat_insurance', 'Insurance', 8, 5.0, true),
    ('cat_debt_payments', 'Debt Payments', 8, 10.0, true),
    ('cat_savings', 'Savings', 7, 15.0, true),
    ('cat_childcare', 'Childcare', 7, 8.0, true),
    ('cat_education', 'Education', 6, 5.0, true),

    -- Moderate (4-5)
    ('cat_dining', 'Dining Out', 4, 8.0, true),
    ('cat_entertainment', 'Entertainment', 3, 5.0, true),
    ('cat_shopping', 'Shopping', 3, 7.0, true),
    ('cat_fitness', 'Fitness & Wellness', 5, 3.0, true),
    ('cat_subscriptions', 'Subscriptions', 4, 3.0, true),

    -- Discretionary (1-3)
    ('cat_travel', 'Travel', 2, 5.0, true),
    ('cat_hobbies', 'Hobbies', 2, 3.0, true),
    ('cat_gifts', 'Gifts & Donations', 3, 3.0, true),
    ('cat_personal_care', 'Personal Care', 4, 3.0, true),
    ('cat_other', 'Other', 1, 2.0, true)
ON CONFLICT (id) DO NOTHING;

-- ============= Category Matching Rules =============

-- Housing
INSERT INTO category_rules (category_id, keywords, merchant_patterns, match_type, priority) VALUES
    ('cat_housing', ARRAY['rent', 'mortgage', 'property', 'landlord', 'lease'], ARRAY['zillow', 'apartments.com', 'realtor'], 'substring', 10);

-- Utilities
INSERT INTO category_rules (category_id, keywords, merchant_patterns, match_type, priority) VALUES
    ('cat_utilities', ARRAY['electric', 'gas', 'water', 'internet', 'cable', 'phone', 'mobile'],
     ARRAY['pge', 'at&t', 'verizon', 'comcast', 'xfinity', 't-mobile', 'sprint'], 'substring', 10);

-- Groceries
INSERT INTO category_rules (category_id, keywords, merchant_patterns, match_type, priority) VALUES
    ('cat_groceries', ARRAY['grocery', 'supermarket', 'market', 'food', 'produce'],
     ARRAY['whole foods', 'trader joes', 'safeway', 'kroger', 'walmart', 'target', 'costco', 'aldi', 'publix', 'wegmans', 'sprouts'], 'substring', 9);

-- Healthcare
INSERT INTO category_rules (category_id, keywords, merchant_patterns, match_type, priority) VALUES
    ('cat_healthcare', ARRAY['pharmacy', 'doctor', 'hospital', 'clinic', 'medical', 'health', 'dental', 'vision'],
     ARRAY['cvs', 'walgreens', 'rite aid', 'kaiser', 'cigna', 'blue cross', 'aetna'], 'substring', 9);

-- Transportation
INSERT INTO category_rules (category_id, keywords, merchant_patterns, match_type, priority) VALUES
    ('cat_transportation', ARRAY['gas', 'fuel', 'station', 'uber', 'lyft', 'taxi', 'parking', 'toll', 'transit', 'metro', 'subway'],
     ARRAY['shell', 'chevron', 'exxon', 'bp', 'mobil', '76', 'arco', 'uber', 'lyft', 'parking'], 'substring', 8);

-- Insurance
INSERT INTO category_rules (category_id, keywords, merchant_patterns, match_type, priority) VALUES
    ('cat_insurance', ARRAY['insurance', 'premium', 'policy'],
     ARRAY['geico', 'progressive', 'state farm', 'allstate', 'farmers', 'usaa'], 'substring', 8);

-- Debt Payments
INSERT INTO category_rules (category_id, keywords, merchant_patterns, match_type, priority) VALUES
    ('cat_debt_payments', ARRAY['loan', 'credit card', 'payment', 'payoff', 'debt'],
     ARRAY['chase', 'bank of america', 'citi', 'discover', 'american express', 'wells fargo', 'capital one'], 'substring', 9);

-- Dining Out
INSERT INTO category_rules (category_id, keywords, merchant_patterns, match_type, priority) VALUES
    ('cat_dining', ARRAY['restaurant', 'cafe', 'coffee', 'diner', 'bistro', 'bar', 'grill', 'pizza', 'burger', 'sushi', 'taco'],
     ARRAY['starbucks', 'mcdonalds', 'chipotle', 'subway', 'panera', 'chick-fil-a', 'taco bell', 'olive garden', 'applebees', 'dominos', 'pizza hut', 'kfc', 'wendys', 'dunkin'], 'substring', 7);

-- Entertainment
INSERT INTO category_rules (category_id, keywords, merchant_patterns, match_type, priority) VALUES
    ('cat_entertainment', ARRAY['movie', 'theater', 'cinema', 'concert', 'game', 'ticket', 'amusement', 'park'],
     ARRAY['amc', 'regal', 'cinemark', 'ticketmaster', 'stubhub', 'disney', 'universal', 'six flags'], 'substring', 6);

-- Subscriptions
INSERT INTO category_rules (category_id, keywords, merchant_patterns, match_type, priority) VALUES
    ('cat_subscriptions', ARRAY['subscription', 'membership', 'monthly', 'annual'],
     ARRAY['netflix', 'spotify', 'hulu', 'disney+', 'amazon prime', 'apple music', 'youtube premium', 'gym', 'planet fitness', 'la fitness'], 'substring', 7);

-- Shopping
INSERT INTO category_rules (category_id, keywords, merchant_patterns, match_type, priority) VALUES
    ('cat_shopping', ARRAY['amazon', 'store', 'shop', 'retail', 'clothes', 'clothing', 'apparel'],
     ARRAY['amazon', 'ebay', 'etsy', 'target', 'macys', 'nordstrom', 'gap', 'old navy', 'h&m', 'zara', 'forever 21', 'tjmaxx', 'marshalls', 'ross'], 'substring', 6);

-- Fitness
INSERT INTO category_rules (category_id, keywords, merchant_patterns, match_type, priority) VALUES
    ('cat_fitness', ARRAY['gym', 'fitness', 'yoga', 'workout', 'sport', 'trainer'],
     ARRAY['planet fitness', 'la fitness', '24 hour fitness', 'equinox', 'crunch', 'orangetheory', 'soulcycle', 'peloton'], 'substring', 5);

-- Travel
INSERT INTO category_rules (category_id, keywords, merchant_patterns, match_type, priority) VALUES
    ('cat_travel', ARRAY['hotel', 'motel', 'flight', 'airline', 'airbnb', 'travel', 'vacation', 'resort'],
     ARRAY['airbnb', 'hotels.com', 'marriott', 'hilton', 'hyatt', 'delta', 'united', 'american airlines', 'southwest', 'expedia', 'booking.com'], 'substring', 5);

-- Personal Care
INSERT INTO category_rules (category_id, keywords, merchant_patterns, match_type, priority) VALUES
    ('cat_personal_care', ARRAY['salon', 'barber', 'spa', 'nails', 'beauty', 'cosmetic', 'haircut'],
     ARRAY['ulta', 'sephora', 'salon', 'barber', 'spa'], 'substring', 4);

-- Education
INSERT INTO category_rules (category_id, keywords, merchant_patterns, match_type, priority) VALUES
    ('cat_education', ARRAY['tuition', 'school', 'university', 'college', 'course', 'book', 'education'],
     ARRAY['coursera', 'udemy', 'skillshare', 'university', 'college', 'barnes & noble', 'chegg'], 'substring', 7);

-- Gifts & Donations
INSERT INTO category_rules (category_id, keywords, merchant_patterns, match_type, priority) VALUES
    ('cat_gifts', ARRAY['gift', 'donation', 'charity', 'nonprofit'],
     ARRAY['red cross', 'salvation army', 'goodwill', 'unicef', 'patreon'], 'substring', 4);

-- Childcare
INSERT INTO category_rules (category_id, keywords, merchant_patterns, match_type, priority) VALUES
    ('cat_childcare', ARRAY['daycare', 'babysitter', 'nanny', 'childcare', 'preschool'],
     ARRAY['kindercare', 'daycare'], 'substring', 8);

-- ============= Default Budget Allocation Template =============
-- This can be used as a starting point for new users

-- 50/30/20 Rule base:
-- Needs (50%): Housing, Utilities, Groceries, Healthcare, Transportation, Insurance
-- Wants (30%): Dining, Entertainment, Shopping, Travel, Hobbies
-- Savings (20%): Savings, Debt Payments

COMMENT ON TABLE categories IS 'System and user-defined expense categories with necessity scores';
COMMENT ON TABLE category_rules IS 'Automatic categorization rules using keywords and patterns';
COMMENT ON COLUMN categories.necessity_score IS 'Priority score 1-10 where 10 is most essential';
COMMENT ON COLUMN categories.default_allocation_percent IS 'Suggested budget allocation percentage';
