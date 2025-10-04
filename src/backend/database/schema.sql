-- BudgetWise Database Schema
-- For Supabase PostgreSQL

-- ============= Users Table =============
-- Extends Supabase auth.users
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    monthly_income DECIMAL(12,2),
    financial_goals TEXT[],
    risk_tolerance TEXT CHECK (risk_tolerance IN ('conservative', 'moderate', 'aggressive')) DEFAULT 'moderate',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============= Categories =============
CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    necessity_score INTEGER CHECK (necessity_score BETWEEN 1 AND 10),
    default_allocation_percent DECIMAL(5,2),
    parent_category_id UUID REFERENCES categories(id),
    is_system BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============= Category Rules =============
-- Rules for automatic categorization
CREATE TABLE IF NOT EXISTS category_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    keywords TEXT[] DEFAULT '{}',
    merchant_patterns TEXT[] DEFAULT '{}',
    match_type TEXT CHECK (match_type IN ('exact', 'substring', 'regex')) DEFAULT 'substring',
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============= User Category Preferences =============
CREATE TABLE IF NOT EXISTS user_category_preferences (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    custom_priority INTEGER CHECK (custom_priority BETWEEN 1 AND 10),
    monthly_limit DECIMAL(12,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, category_id)
);

-- ============= User Merchant Overrides =============
-- User-specific merchant to category mappings
CREATE TABLE IF NOT EXISTS user_merchant_overrides (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    merchant TEXT NOT NULL,
    category_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, merchant)
);

-- ============= Budgets =============
CREATE TABLE IF NOT EXISTS budgets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    month TEXT NOT NULL, -- Format: "2025-10"
    total_income DECIMAL(12,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, month)
);

-- ============= Budget Allocations =============
CREATE TABLE IF NOT EXISTS budget_allocations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    budget_id UUID REFERENCES budgets(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id),
    allocated_amount DECIMAL(12,2),
    spent_amount DECIMAL(12,2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(budget_id, category_id)
);

-- ============= Expenses =============
CREATE TABLE IF NOT EXISTS expenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    amount DECIMAL(12,2) NOT NULL,
    category_id UUID REFERENCES categories(id),
    description TEXT,
    merchant TEXT,
    date TIMESTAMPTZ DEFAULT NOW(),
    is_recurring BOOLEAN DEFAULT false,
    ai_suggested_category UUID REFERENCES categories(id),
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============= Recurring Expenses =============
CREATE TABLE IF NOT EXISTS recurring_expenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    amount DECIMAL(12,2) NOT NULL,
    category_id UUID REFERENCES categories(id),
    description TEXT,
    frequency TEXT CHECK (frequency IN ('daily', 'weekly', 'monthly', 'yearly')),
    start_date TIMESTAMPTZ NOT NULL,
    end_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============= Chat Messages =============
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role TEXT CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

-- ============= Indexes =============
-- Performance optimization indexes

-- Expenses indexes
CREATE INDEX IF NOT EXISTS idx_expenses_user_date ON expenses(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category_id);
CREATE INDEX IF NOT EXISTS idx_expenses_merchant ON expenses(merchant);

-- Budget indexes
CREATE INDEX IF NOT EXISTS idx_budgets_user_month ON budgets(user_id, month);
CREATE INDEX IF NOT EXISTS idx_budget_allocations_budget ON budget_allocations(budget_id);

-- Category indexes
CREATE INDEX IF NOT EXISTS idx_categories_name ON categories(name);
CREATE INDEX IF NOT EXISTS idx_category_rules_category ON category_rules(category_id);

-- User overrides index
CREATE INDEX IF NOT EXISTS idx_user_merchant_overrides ON user_merchant_overrides(user_id, merchant);

-- ============= Row Level Security (RLS) =============
-- Enable RLS on all tables

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE budgets ENABLE ROW LEVEL SECURITY;
ALTER TABLE budget_allocations ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_category_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_merchant_overrides ENABLE ROW LEVEL SECURITY;
ALTER TABLE recurring_expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

-- RLS Policies

-- Users can only see their own data
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (auth.uid() = id);

-- Expenses policies
CREATE POLICY "Users can view own expenses" ON expenses
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own expenses" ON expenses
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own expenses" ON expenses
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own expenses" ON expenses
    FOR DELETE USING (auth.uid() = user_id);

-- Budget policies
CREATE POLICY "Users can view own budgets" ON budgets
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own budgets" ON budgets
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own budgets" ON budgets
    FOR UPDATE USING (auth.uid() = user_id);

-- Budget allocations policies (through budget)
CREATE POLICY "Users can view own budget allocations" ON budget_allocations
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM budgets
            WHERE budgets.id = budget_allocations.budget_id
            AND budgets.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can manage own budget allocations" ON budget_allocations
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM budgets
            WHERE budgets.id = budget_allocations.budget_id
            AND budgets.user_id = auth.uid()
        )
    );

-- Categories are public (read-only for users)
CREATE POLICY "Anyone can view categories" ON categories
    FOR SELECT USING (true);

-- User preferences policies
CREATE POLICY "Users can manage own preferences" ON user_category_preferences
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own overrides" ON user_merchant_overrides
    FOR ALL USING (auth.uid() = user_id);

-- Chat messages policies
CREATE POLICY "Users can view own chat messages" ON chat_messages
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own chat messages" ON chat_messages
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ============= Functions & Triggers =============

-- Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_budgets_updated_at BEFORE UPDATE ON budgets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_budget_allocations_updated_at BEFORE UPDATE ON budget_allocations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_category_preferences_updated_at BEFORE UPDATE ON user_category_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_expenses_updated_at BEFORE UPDATE ON expenses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
