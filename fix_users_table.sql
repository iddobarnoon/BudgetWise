-- Remove foreign key constraint from users table for testing
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_id_fkey;

-- Now we can insert test users directly
INSERT INTO users (id, email, full_name, monthly_income, financial_goals, risk_tolerance)
VALUES
  ('db8f4c2a-3e5f-4d9b-8a6c-1f7e9d2b4a8c', 'test@budgetwise.com', 'Test User', 10000.00, ARRAY['Save for emergency fund'], 'moderate')
ON CONFLICT (id) DO NOTHING;

-- Verify
SELECT * FROM users;
