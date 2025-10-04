# Update .env with Database Password

## You need to add your Supabase database password to the `.env` file

### Where to find your database password:

1. Go to: https://supabase.com/dashboard/project/mjwuxawseluajqduwuru/settings/database
2. Look for **Database Password** section
3. If you don't see it, click "Reset Database Password"
4. Copy the password

### Update .env file:

Open `/Users/itamaramsalem/Desktop/BudgetWise/.env` and add this line:

```bash
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD_HERE@db.mjwuxawseluajqduwuru.supabase.co:5432/postgres
```

Replace `YOUR_PASSWORD_HERE` with your actual database password.

### Example:

If your password is `MySecretPass123`, the line would be:

```bash
DATABASE_URL=postgresql://postgres:MySecretPass123@db.mjwuxawseluajqduwuru.supabase.co:5432/postgres
```

---

## Once you've added the password:

Run:
```bash
python3 init_database.py
```

This will:
1. Test the database connection
2. Create all tables automatically
3. Seed 20 categories and matching rules
4. Be ready to use!

---

## Alternative: Use the connection string you already have

You mentioned:
```
postgresql://postgres:[YOUR-PASSWORD]@db.mjwuxawseluajqduwuru.supabase.co:5432/postgres
```

Just replace `[YOUR-PASSWORD]` with your actual password and add it to .env as DATABASE_URL
