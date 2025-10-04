#!/bin/bash

echo "======================================================================"
echo "Testing Budget Engine API with Database"
echo "======================================================================"

# Generate a UUID for test user
USER_ID=$(python3 -c "import uuid; print(str(uuid.uuid4()))")

echo ""
echo "Test User ID: $USER_ID"
echo ""

# Test 1: Create Budget
echo "======================================================================"
echo "TEST 1: Create Budget"
echo "======================================================================"
curl -X POST http://localhost:8003/budget/create \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"month\": \"2025-10\",
    \"income\": 5000,
    \"goals\": [\"Save 20% for emergency fund\"]
  }" | python3 -m json.tool

echo ""
echo ""

# Test 2: Get Budget Summary
echo "======================================================================"
echo "TEST 2: Get Budget Summary"
echo "======================================================================"
curl "http://localhost:8003/budget/summary?user_id=$USER_ID&month=2025-10" | python3 -m json.tool

echo ""
echo ""

# Get a category ID for testing
CATEGORY_ID=$(python3 -c "from supabase import create_client; import os; from dotenv import load_dotenv; load_dotenv(); s = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY')); cats = s.table('categories').select('id').limit(1).execute().data; print(cats[0]['id'] if cats else 'none')")

echo "Test Category ID: $CATEGORY_ID"
echo ""

# Test 3: Check Purchase (should fit)
echo "======================================================================"
echo "TEST 3: Check Purchase - Should FIT Budget"
echo "======================================================================"
curl -X POST http://localhost:8003/budget/check-purchase \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"amount\": 100,
    \"category_id\": \"$CATEGORY_ID\",
    \"month\": \"2025-10\"
  }" | python3 -m json.tool

echo ""
echo ""

# Test 4: Check Purchase (should NOT fit)
echo "======================================================================"
echo "TEST 4: Check Purchase - Should EXCEED Budget"
echo "======================================================================"
curl -X POST http://localhost:8003/budget/check-purchase \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"amount\": 2000,
    \"category_id\": \"$CATEGORY_ID\",
    \"month\": \"2025-10\"
  }" | python3 -m json.tool

echo ""
echo ""

# Test 5: Update Spent Amount
echo "======================================================================"
echo "TEST 5: Update Spent Amount"
echo "======================================================================"
curl -X PUT http://localhost:8003/budget/update-spent \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"category_id\": \"$CATEGORY_ID\",
    \"amount\": 50,
    \"month\": \"2025-10\"
  }" | python3 -m json.tool

echo ""
echo ""

# Test 6: Get Suggestions
echo "======================================================================"
echo "TEST 6: Get Reallocation Suggestions"
echo "======================================================================"
curl "http://localhost:8003/budget/suggestions?user_id=$USER_ID&month=2025-10" | python3 -m json.tool

echo ""
echo "======================================================================"
echo "✅ All tests complete!"
echo "======================================================================"
echo ""
echo "Open Swagger UI: http://localhost:8003/docs"
echo ""
