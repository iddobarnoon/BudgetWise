# Budget Engine Service

Intelligent budget creation and management service with smart allocation algorithms.

## Features

- **Smart Budget Creation**: AI-powered budget generation based on income, goals, and spending patterns
- **Multiple Allocation Strategies**: 50/30/20 rule, 70/20/10 rule, aggressive savings, debt payoff, and more
- **Purchase Validation**: Check if purchases fit within budget before spending
- **Reallocation Suggestions**: Smart recommendations to optimize budget based on actual spending
- **Overspending Detection**: Automatic alerts when categories exceed budget
- **Goal-Based Budgeting**: Adjusts allocations based on financial goals

## API Endpoints

### POST `/budget/create`
Generate a monthly budget based on income and goals.

**Request Body:**
```json
{
  "user_id": "user_123",
  "month": "2025-10",
  "income": 5000.00,
  "goals": ["Save 20% for emergency fund", "Pay off credit card debt"]
}
```

**Response:**
```json
{
  "id": "budget_456",
  "user_id": "user_123",
  "month": "2025-10",
  "total_income": 5000.00,
  "allocations": [
    {
      "category_id": "cat_housing",
      "allocated_amount": 1500.00,
      "spent_amount": 0,
      "remaining_amount": 1500.00
    }
  ],
  "created_at": "2025-10-04T12:00:00Z",
  "updated_at": "2025-10-04T12:00:00Z"
}
```

### POST `/budget/check-purchase`
Validate if a purchase fits within the budget.

**Request Body:**
```json
{
  "user_id": "user_123",
  "amount": 200.00,
  "category_id": "cat_dining",
  "month": "2025-10"
}
```

**Response:**
```json
{
  "fits_budget": false,
  "remaining_in_category": 150.00,
  "percentage_of_category": 133.33,
  "alternative_options": [
    "Wait until next month when budget resets",
    "Reduce purchase amount by $50.00 to stay in budget",
    "Consider using funds from: Entertainment, Hobbies"
  ],
  "warning": "This exceeds your budget by $50.00"
}
```

### GET `/budget/summary?user_id={id}&month={YYYY-MM}`
Get current budget state with spending breakdown.

**Response:**
```json
{
  "total_budget": 5000.00,
  "total_spent": 3200.00,
  "total_remaining": 1800.00,
  "categories": [
    {
      "category_id": "cat_housing",
      "allocated_amount": 1500.00,
      "spent_amount": 1500.00,
      "remaining_amount": 0
    }
  ],
  "overspent_categories": ["cat_dining"]
}
```

### PUT `/budget/update-spent`
Update spent amount when an expense is logged.

**Request Body:**
```json
{
  "user_id": "user_123",
  "category_id": "cat_groceries",
  "amount": 75.50,
  "month": "2025-10"
}
```

**Response:**
```json
{
  "category_id": "cat_groceries",
  "allocated_amount": 600.00,
  "spent_amount": 425.50,
  "remaining_amount": 174.50
}
```

### GET `/budget/suggestions?user_id={id}&month={YYYY-MM}`
Get smart reallocation suggestions.

**Response:**
```json
[
  {
    "type": "reallocation",
    "from_category": "Entertainment",
    "to_category": "Dining Out",
    "amount": 150.00,
    "reason": "You've overspent on Dining Out by $150.00, but have $400.00 remaining in Entertainment"
  }
]
```

## Budget Allocation Strategies

### 1. 50/30/20 Rule (Default)
- **50% Needs**: Housing, utilities, groceries, healthcare, transportation
- **30% Wants**: Dining, entertainment, shopping, hobbies
- **20% Savings**: Savings accounts, investments, emergency fund

### 2. 70/20/10 Rule
- **70% Living Expenses**: All regular expenses
- **20% Savings**: Future planning
- **10% Debt Repayment**: Pay off debt faster

### 3. Aggressive Savings
- **40% Savings**: Maximize savings rate
- **60% Expenses**: Minimized discretionary spending
- Best for: Building emergency fund, early retirement

### 4. Debt Payoff Strategy
- **30% Debt Payments**: Accelerated debt repayment
- **60% Essentials**: Maintain necessities
- **10% Discretionary**: Minimal wants
- Best for: Getting out of debt quickly

### 5. Balanced Strategy
- Proportional allocation based on necessity scores
- Considers user preferences
- Adjusts to spending patterns

### 6. Zero-Based Budgeting
- Every dollar has a job
- Fixed expenses first, then variable
- No money unallocated

### 7. Envelope Method
- Fixed amount per category
- Once envelope is empty, no more spending
- Great for controlling discretionary spending

## How Budget Creation Works

```python
1. Analyze Historical Spending
   ↓
2. Get Category Priorities (from Ranking System)
   ↓
3. Determine Strategy Based on Goals
   ↓
4. Calculate Allocations
   ↓
5. Apply User Preferences
   ↓
6. Rebalance to Fit Income
   ↓
7. Save to Database
```

## Goal-Based Adjustments

The engine automatically adjusts allocations based on goals:

| Goal | Adjustments |
|------|-------------|
| "Save for emergency fund" | Savings ↑ 150%, Entertainment ↓ 70% |
| "Pay off debt" | Debt payments ↑ 150%, Discretionary ↓ 50% |
| "Invest more" | Savings ↑ 130% |

## Running the Service

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your Supabase credentials

# Run the service
cd src/backend/components/budget-engine
python app.py

# Or with uvicorn
uvicorn app:app --host 0.0.0.0 --port 8003 --reload
```

## Testing

```bash
# Run comprehensive test suite
python3 test_budget.py

# With pytest
pytest test_budget.py -v
```

### Test Coverage

✅ **10 Test Cases:**
1. Budget Allocation Calculation
2. 50/30/20 Budget Rule
3. Purchase Validation
4. Percentage Calculation
5. Budget Summary Generation
6. Reallocation Suggestions
7. Goal-Based Allocation
8. Overspent Detection
9. Income Rebalancing
10. Spending Pattern Analysis

**All tests passing!** 🎉

## Integration with Other Services

### With Ranking System
```python
# Get category priorities for budget allocation
priorities = await ranking_service.get_priority_order(user_id)

# Budget engine uses these priorities
budget = await budget_engine.create_budget(user_id, month, income)
```

### With AI Layer
```python
# AI asks budget engine before recommendations
purchase_check = await budget_engine.check_purchase(
    user_id, amount, category_id, month
)

if not purchase_check["fits_budget"]:
    ai_response = "This doesn't fit your budget. " + purchase_check["warning"]
```

### With Expense Tracking
```python
# When expense is logged, update budget
await budget_engine.update_spent_amount(
    user_id, category_id, amount, month
)
```

## Database Tables Used

- `budgets`: Monthly budget records
- `budget_allocations`: Category-wise allocations
- `expenses`: Historical spending for pattern analysis
- `user_category_preferences`: Custom priorities

## Architecture

```
Client Request
    ↓
API Endpoint (routes.py)
    ↓
Budget Engine (main.py)
    ├── Analyze spending patterns
    ├── Select allocation strategy (algorithms.py)
    ├── Calculate allocations
    ├── Apply user preferences
    └── Rebalance to income
    ↓
Database (Supabase)
    ↓
Response with budget plan
```

## Example Flow: Creating a Budget

```bash
# 1. User provides income and goals
POST /budget/create
{
  "user_id": "user_123",
  "month": "2025-10",
  "income": 5000,
  "goals": ["Save 20% for emergency fund"]
}

# 2. Engine analyzes historical spending
# 3. Selects aggressive savings strategy
# 4. Calculates allocations:
#    - Savings: $2000 (40%)
#    - Housing: $1500 (30%)
#    - Groceries: $750 (15%)
#    - Transportation: $500 (10%)
#    - Entertainment: $250 (5%)

# 5. Returns budget plan
```

## Key Algorithms

### Rebalancing Algorithm
```python
if total_allocated > income:
    ratio = income / total_allocated
    for allocation in allocations:
        allocation.amount *= ratio
```

### Purchase Validation
```python
remaining = allocated - spent
fits = purchase_amount <= remaining
percentage = (purchase_amount / allocated) * 100
```

### Reallocation Detection
```python
overspent = [cat for cat in categories if spent > allocated]
underspent = [cat for cat in categories if remaining > allocated * 0.5]

# Suggest moving funds from underspent to overspent
```

## Performance Considerations

- Categories and rules cached in memory
- Historical analysis limited to last 3 months (200 expenses)
- Allocation calculations use Decimal for precision
- Database queries optimized with proper indexes

## Error Handling

- Returns 404 if budget not found for month
- Returns 400 for invalid amounts (negative, zero)
- Returns 500 for database errors
- Provides user-friendly error messages
