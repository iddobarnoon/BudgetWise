# Supabase Database Setup Guide

## ✅ Step 1: Credentials Configured
Your `.env` file has been created with:
- SUPABASE_URL: https://mjwuxawseluajqduwuru.supabase.co
- SUPABASE_KEY: (configured)

## 📋 Step 2: Create Database Tables

### Option A: Using Supabase Dashboard (Recommended)

1. **Open SQL Editor:**
   - Go to: https://supabase.com/dashboard/project/mjwuxawseluajqduwuru/sql/new

2. **Run Schema SQL:**
   - Click "New Query"
   - Copy ALL contents from: `src/backend/database/schema.sql`
   - Paste into the SQL editor
   - Click **"Run"** button (or press Cmd/Ctrl + Enter)
   - Wait for ✅ Success message

3. **Run Seed Data SQL:**
   - Click "New Query" again
   - Copy ALL contents from: `src/backend/database/seed_data.sql`
   - Paste into the SQL editor
   - Click **"Run"** button
   - Wait for ✅ Success message

### Option B: Quick Start (Copy-Paste Ready)

I'll provide you the SQL in the terminal - you can copy it directly.

## 🔍 Step 3: Verify Setup

After running the SQL, run:
```bash
python3 setup_database.py
```

You should see:
```
✅ Connection successful!
✅ Categories table exists with 20 records
```

## 📊 What Gets Created

### Tables (12 total):
- `users` - User profiles
- `categories` - 20 expense categories
- `category_rules` - Matching rules for auto-categorization
- `user_category_preferences` - Custom user priorities
- `user_merchant_overrides` - User-specific merchant mappings
- `budgets` - Monthly budgets
- `budget_allocations` - Category allocations
- `expenses` - Expense records
- `recurring_expenses` - Recurring expenses
- `chat_messages` - Chat history

### Initial Data:
- **20 Categories**: Housing, Utilities, Groceries, Dining, etc.
- **15+ Matching Rules**: 100+ merchant patterns
- Indexes for performance
- Row Level Security policies

## 🚀 Step 4: Start Services

Once tables are created, restart services:

```bash
# Kill standalone service
# (Press Ctrl+C in the terminal running app_standalone.py)

# Start full Budget Engine with database
cd src/backend/components/budget-engine
python3 app.py
```

## ❓ Troubleshooting

### "Could not find table" error
- Make sure you ran `schema.sql` first
- Check Supabase Dashboard → Table Editor to see if tables exist

### "Permission denied" error
- Make sure you're using the `anon` key (not service_role)
- Check Row Level Security policies were created

### "Syntax error" in SQL
- Copy the ENTIRE file contents
- Don't modify the SQL
- Run schema.sql BEFORE seed_data.sql

## 📁 File Locations

- Schema SQL: `/src/backend/database/schema.sql`
- Seed Data SQL: `/src/backend/database/seed_data.sql`
- Setup Script: `/setup_database.py`

---

## Ready to Proceed?

Once you've run both SQL files in Supabase Dashboard, let me know and I'll:
1. Test the database connection
2. Restart the Budget Engine with full database support
3. Show you how to create budgets and track expenses
