#!/bin/bash

echo "======================================================================"
echo "Testing BudgetWise Services"
echo "======================================================================"

USER_ID="db8f4c2a-3e5f-4d9b-8a6c-1f7e9d2b4a8c"

echo ""
echo "1️⃣  RANKING SYSTEM - Get Categories"
echo "======================================================================"
curl "http://localhost:8002/ranking/categories?user_id=$USER_ID" | python3 -m json.tool | head -40

echo ""
echo ""
echo "2️⃣  RANKING SYSTEM - Classify Expense (Starbucks)"
echo "======================================================================"
curl -X POST http://localhost:8002/ranking/classify \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"description\": \"Starbucks coffee\",
    \"amount\": 5.50,
    \"merchant\": \"Starbucks\"
  }" | python3 -m json.tool

echo ""
echo ""
echo "3️⃣  BUDGET ENGINE - Create Budget"
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
echo "4️⃣  BUDGET ENGINE - Get Budget Summary"
echo "======================================================================"
curl "http://localhost:8003/budget/summary?user_id=$USER_ID&month=2025-10" | python3 -m json.tool

echo ""
echo ""
echo "5️⃣  BUDGET ENGINE - Check Purchase"
echo "======================================================================"
curl -X POST http://localhost:8003/budget/check-purchase \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"amount\": 100,
    \"category_id\": \"95f4b1e7-15f5-4a82-9d7d-d44472445f10\",
    \"month\": \"2025-10\"
  }" | python3 -m json.tool

echo ""
echo "======================================================================"
echo "✅ Tests Complete!"
echo "======================================================================"
echo ""
echo "📖 Swagger UIs:"
echo "   Budget Engine:  http://localhost:8003/docs"
echo "   Ranking System: http://localhost:8002/docs"
echo ""
