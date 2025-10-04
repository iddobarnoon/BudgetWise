-- Disable Row Level Security for Testing
-- This allows testing without authentication
-- WARNING: Re-enable RLS in production!

-- Disable RLS on main tables
ALTER TABLE budgets DISABLE ROW LEVEL SECURITY;
ALTER TABLE budget_allocations DISABLE ROW LEVEL SECURITY;
ALTER TABLE expenses DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_category_preferences DISABLE ROW LEVEL SECURITY;
ALTER TABLE user_merchant_overrides DISABLE ROW LEVEL SECURITY;

-- Optional: Also disable on users table for testing
-- ALTER TABLE users DISABLE ROW LEVEL SECURITY;

-- Note: Categories already allows public read access
