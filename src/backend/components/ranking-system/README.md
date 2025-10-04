# Ranking System Service

AI-powered expense categorization and priority ranking service for BudgetWise.

## Features

- **Automatic Categorization**: Classifies expenses based on merchant names and descriptions
- **User Overrides**: Learns from user corrections for personalized categorization
- **Confidence Scoring**: Provides confidence scores for categorization decisions
- **Priority Ranking**: Orders categories by necessity for budget allocation
- **Custom Priorities**: Users can customize category importance

## API Endpoints

### GET `/ranking/categories`
Get all categories with user's custom priorities.

**Query Parameters:**
- `user_id` (required): User ID

**Response:**
```json
[
  {
    "id": "cat_groceries",
    "name": "Groceries",
    "necessity_score": 9,
    "default_allocation_percent": 15.0,
    "is_system": true
  }
]
```

### POST `/ranking/classify`
Classify an expense into a category.

**Request Body:**
```json
{
  "description": "Starbucks coffee",
  "amount": 5.50,
  "user_id": "user_123",
  "merchant": "Starbucks"
}
```

**Response:**
```json
{
  "category_id": "cat_dining",
  "category_name": "Dining Out",
  "necessity_score": 4,
  "confidence": 0.95,
  "alternatives": [
    ["Groceries", 0.3],
    ["Other", 0.1]
  ]
}
```

### GET `/ranking/priorities`
Get categories ordered by priority for budget allocation.

**Query Parameters:**
- `user_id` (required): User ID

**Response:**
```json
[
  {
    "id": "cat_housing",
    "name": "Housing",
    "necessity_score": 10,
    ...
  }
]
```

### PUT `/ranking/priorities/{category_id}`
Update user's custom priority for a category.

**Query Parameters:**
- `user_id` (required): User ID

**Request Body:**
```json
{
  "custom_priority": 8,
  "monthly_limit": 500.00
}
```

### POST `/ranking/correct`
Correct a miscategorized expense.

**Query Parameters:**
- `user_id` (required): User ID

**Request Body:**
```json
{
  "merchant": "Whole Foods",
  "correct_category_id": "cat_groceries"
}
```

### POST `/ranking/process-expense`
Process and categorize an expense.

**Request Body:**
```json
{
  "user_id": "user_123",
  "merchant": "Shell Gas Station",
  "description": "Gas fill-up",
  "amount": 45.00,
  "expense_id": "expense_456"
}
```

**Response:**
```json
{
  "expense_id": "expense_456",
  "category_id": "cat_transportation",
  "category_name": "Transportation",
  "confidence": 0.92,
  "necessity_score": 8,
  "alternatives": []
}
```

## How It Works

### Merchant Normalization
1. Converts to lowercase
2. Removes numbers and special characters
3. Standardizes spacing
4. Example: "Trader Joe's #122" → "trader joes"

### Categorization Logic
1. **User Overrides First**: Check if user has manually set this merchant
2. **Rule Matching**: Score each category rule based on:
   - Keyword matching (exact, substring, or regex)
   - Merchant pattern matching
   - Priority boosting
3. **Description Matching**: Also check description text (80% weight)
4. **Confidence Calculation**: Based on score gaps between top candidates

### Confidence Score
```python
confidence = top_score * (1 - (second_score / top_score))
```
- Higher gap between top two = higher confidence
- Range: 0.0 to 1.0

## Running the Service

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your Supabase credentials

# Run the service
cd src/backend/components/ranking-system
python app.py

# Or with uvicorn
uvicorn app:app --host 0.0.0.0 --port 8002 --reload
```

## Testing

```bash
# Run tests
python test_ranking.py

# Or with pytest
pytest test_ranking.py -v
```

## Categories

### Essential (9-10)
- Housing (10)
- Utilities (10)
- Groceries (9)
- Healthcare (9)
- Transportation (8)

### Important (6-8)
- Insurance (8)
- Debt Payments (8)
- Savings (7)
- Education (6)

### Moderate (4-5)
- Dining Out (4)
- Fitness (5)
- Subscriptions (4)

### Discretionary (1-3)
- Travel (2)
- Entertainment (3)
- Shopping (3)
- Hobbies (2)
- Other (1)

## Database Tables Used

- `categories`: System and custom categories
- `category_rules`: Matching rules (keywords, patterns)
- `user_category_preferences`: User custom priorities
- `user_merchant_overrides`: User-specific merchant mappings
- `expenses`: Expense records with categorization

## Architecture

```
Client Request
    ↓
API Endpoint (routes.py)
    ↓
RankingSystem (main.py)
    ├── normalize_merchant()
    ├── apply_user_overrides()
    ├── compute_match_score()
    └── rank_categories()
    ↓
Database (Supabase)
    ↓
Response with category + confidence
```
