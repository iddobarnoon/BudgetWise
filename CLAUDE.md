# BudgetWise - Microservice Architecture Documentation

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Data Flow](#data-flow)
3. [Data Models](#data-models)
4. [Service APIs](#service-apis)
5. [Implementation Roadmap](#implementation-roadmap)
6. [Best Practices & Scaling](#best-practices--scaling)

---

## System Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│                  (Web UI + Voice Interface)                  │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTP/WebSocket
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                       API Gateway                            │
│                  (FastAPI/Kong/Nginx)                        │
└──┬──────────────┬──────────────┬───────────────┬───────────┘
   │              │              │               │
   │ Auth         │ Budget       │ Expense       │ Chat
   ▼              ▼              ▼               ▼
┌──────────┐  ┌──────────┐  ┌──────────────┐  ┌──────────────┐
│   Auth   │  │  Budget  │  │   Ranking    │  │   AI Layer   │
│ Service  │  │  Engine  │  │   System     │  │   (LLM)      │
└─────┬────┘  └────┬─────┘  └──────┬───────┘  └──────┬───────┘
      │            │               │                  │
      │            │               │                  │
      └────────────┴───────────────┴──────────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │     Supabase     │
                  │    PostgreSQL    │
                  └──────────────────┘
```

### Service Descriptions

| Service | Responsibility | Tech Stack |
|---------|---------------|------------|
| **Frontend** | User interface, chat/voice input, visualization | React/Next.js, WebSockets, Web Speech API |
| **API Gateway** | Request routing, rate limiting, auth validation | FastAPI/Kong/Traefik |
| **Auth Service** | JWT generation, session management, user registration | FastAPI + Supabase Auth |
| **Budget Engine** | Budget creation, purchase validation, financial planning | Python FastAPI |
| **Ranking System** | Category classification, necessity scoring, priority rules | Python FastAPI |
| **AI Layer** | NLP, expense categorization, purchase recommendations | LangChain/OpenAI/Anthropic |
| **Supabase** | Data persistence, real-time subscriptions | PostgreSQL + Supabase APIs |

---

## Data Flow

### 1. User Registration & Authentication
```
User → Frontend → Auth Service → Supabase
                      ↓
                  JWT Token → Frontend
```

### 2. Budget Creation
```
User Input → Frontend → Budget Engine
                            ↓
                    Ranking System (get categories)
                            ↓
                    Generate Budget → Supabase
                            ↓
                    Budget Response → Frontend
```

### 3. Purchase Decision Flow
```
User Question → Frontend → AI Layer
  "Should I buy X?"           ↓
                         Extract expense details
                              ↓
                         Budget Engine (check_purchase)
                              ↓
                         Ranking System (get category priority)
                              ↓
                         Generate recommendation
                              ↓
                         Response → Frontend
```

### 4. Expense Logging
```
User Input → AI Layer → Parse expense
                           ↓
                    Ranking System (categorize)
                           ↓
                    Supabase (store expense)
                           ↓
                    Budget Engine (update remaining budget)
```

---

## Data Models

### Core Schema (Pydantic Models)

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from decimal import Decimal

# ============= User & Auth =============

class User(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    monthly_income: Decimal
    financial_goals: List[str] = []
    risk_tolerance: Literal["conservative", "moderate", "aggressive"] = "moderate"

class Session(BaseModel):
    user_id: str
    token: str
    expires_at: datetime

# ============= Categories & Ranking =============

class Category(BaseModel):
    id: str
    name: str
    necessity_score: int = Field(..., ge=1, le=10)  # 1=luxury, 10=essential
    default_allocation_percent: float
    parent_category: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "id": "cat_001",
                "name": "Groceries",
                "necessity_score": 9,
                "default_allocation_percent": 15.0
            }
        }

class UserCategoryPreference(BaseModel):
    user_id: str
    category_id: str
    custom_priority: int = Field(..., ge=1, le=10)
    monthly_limit: Optional[Decimal] = None

# ============= Expenses =============

class Expense(BaseModel):
    id: str
    user_id: str
    amount: Decimal
    category_id: str
    description: str
    date: datetime
    is_recurring: bool = False
    ai_suggested_category: Optional[str] = None
    confidence_score: Optional[float] = None

class RecurringExpense(BaseModel):
    id: str
    user_id: str
    amount: Decimal
    category_id: str
    description: str
    frequency: Literal["daily", "weekly", "monthly", "yearly"]
    start_date: datetime
    end_date: Optional[datetime] = None

# ============= Budget =============

class BudgetPlan(BaseModel):
    id: str
    user_id: str
    month: str  # "2025-10"
    total_income: Decimal
    allocations: List["CategoryAllocation"]
    created_at: datetime
    updated_at: datetime

class CategoryAllocation(BaseModel):
    category_id: str
    allocated_amount: Decimal
    spent_amount: Decimal = Decimal("0")
    remaining_amount: Decimal

class BudgetSummary(BaseModel):
    total_budget: Decimal
    total_spent: Decimal
    total_remaining: Decimal
    categories: List[CategoryAllocation]
    overspent_categories: List[str] = []

# ============= AI Responses =============

class PurchaseRecommendation(BaseModel):
    decision: Literal["buy", "wait", "dont_buy"]
    reason: str
    alternative_suggestions: List[str] = []
    impact_on_budget: str
    category: str
    amount: Decimal

class ChatMessage(BaseModel):
    id: str
    user_id: str
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime
    metadata: Optional[dict] = None  # Store expense/budget refs
```

### Database Schema (Supabase Tables)

```sql
-- Users table (extended from Supabase auth)
CREATE TABLE users (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    monthly_income DECIMAL(12,2),
    financial_goals TEXT[],
    risk_tolerance TEXT CHECK (risk_tolerance IN ('conservative', 'moderate', 'aggressive')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Categories (predefined + custom)
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    necessity_score INTEGER CHECK (necessity_score BETWEEN 1 AND 10),
    default_allocation_percent DECIMAL(5,2),
    parent_category_id UUID REFERENCES categories(id),
    is_system BOOLEAN DEFAULT true
);

-- User category preferences
CREATE TABLE user_category_preferences (
    user_id UUID REFERENCES users(id),
    category_id UUID REFERENCES categories(id),
    custom_priority INTEGER CHECK (custom_priority BETWEEN 1 AND 10),
    monthly_limit DECIMAL(12,2),
    PRIMARY KEY (user_id, category_id)
);

-- Budgets
CREATE TABLE budgets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    month TEXT NOT NULL,
    total_income DECIMAL(12,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, month)
);

-- Budget allocations
CREATE TABLE budget_allocations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    budget_id UUID REFERENCES budgets(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id),
    allocated_amount DECIMAL(12,2),
    spent_amount DECIMAL(12,2) DEFAULT 0,
    UNIQUE(budget_id, category_id)
);

-- Expenses
CREATE TABLE expenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    amount DECIMAL(12,2) NOT NULL,
    category_id UUID REFERENCES categories(id),
    description TEXT,
    date TIMESTAMPTZ DEFAULT NOW(),
    is_recurring BOOLEAN DEFAULT false,
    ai_suggested_category UUID REFERENCES categories(id),
    confidence_score DECIMAL(3,2)
);

-- Chat history
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    role TEXT CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);
```

---

## Service APIs

### 1. Auth Service

```python
class AuthService:
    """Handles user authentication and session management"""

    async def register_user(
        self,
        email: str,
        password: str,
        full_name: str
    ) -> User:
        """
        Register new user with Supabase Auth
        Returns: User object with JWT token
        """
        pass

    async def login(self, email: str, password: str) -> Session:
        """
        Authenticate user and create session
        Returns: Session with JWT token
        """
        pass

    async def validate_token(self, token: str) -> User:
        """
        Validate JWT and return user context
        Raises: AuthenticationError if invalid
        """
        pass

    async def logout(self, token: str) -> bool:
        """Invalidate session token"""
        pass
```

**API Endpoints:**
```
POST   /auth/register
POST   /auth/login
POST   /auth/logout
GET    /auth/me
```

---

### 2. Ranking System

```python
class RankingService:
    """Categorizes and ranks expenses by necessity"""

    async def get_categories(self, user_id: str) -> List[Category]:
        """
        Get all categories with user's custom priorities
        Merges system categories with user preferences
        """
        pass

    async def classify_expense(
        self,
        description: str,
        amount: Decimal,
        user_id: str
    ) -> tuple[Category, float]:
        """
        AI-powered expense categorization
        Returns: (Category, confidence_score)
        Uses: LLM + historical user patterns
        """
        pass

    async def get_priority_order(
        self,
        user_id: str,
        budget_constraints: BudgetSummary
    ) -> List[Category]:
        """
        Returns categories ordered by priority for budget allocation
        Factors: necessity_score, user preferences, spending patterns
        """
        pass

    async def update_user_priority(
        self,
        user_id: str,
        category_id: str,
        new_priority: int
    ) -> UserCategoryPreference:
        """Allow users to customize category importance"""
        pass
```

**API Endpoints:**
```
GET    /ranking/categories?user_id={id}
POST   /ranking/classify
GET    /ranking/priorities?user_id={id}
PUT    /ranking/priorities/{category_id}
```

**Example Request/Response:**
```json
POST /ranking/classify
{
    "description": "Weekly grocery shopping at Whole Foods",
    "amount": 150.00,
    "user_id": "user_123"
}

Response:
{
    "category": {
        "id": "cat_groceries",
        "name": "Groceries",
        "necessity_score": 9
    },
    "confidence": 0.95,
    "alternative_categories": []
}
```

---

### 3. Budget Engine

```python
class BudgetEngine:
    """Generates and manages personalized budgets"""

    async def create_budget(
        self,
        user_id: str,
        month: str,
        income: Decimal,
        goals: List[str]
    ) -> BudgetPlan:
        """
        Generate monthly budget using:
        - User income
        - Historical spending patterns
        - Category priorities (from Ranking System)
        - Financial goals (save X%, pay off debt, etc.)
        """
        pass

    async def check_purchase(
        self,
        user_id: str,
        amount: Decimal,
        category_id: str,
        month: str
    ) -> dict:
        """
        Validate if purchase fits budget
        Returns: {
            "fits_budget": bool,
            "remaining_in_category": Decimal,
            "percentage_of_category": float,
            "alternative_options": List[str]
        }
        """
        pass

    async def get_budget_summary(
        self,
        user_id: str,
        month: str
    ) -> BudgetSummary:
        """Get current budget state with spending breakdown"""
        pass

    async def update_spent_amount(
        self,
        user_id: str,
        category_id: str,
        amount: Decimal,
        month: str
    ) -> CategoryAllocation:
        """Update spent amount when expense is logged"""
        pass

    async def suggest_reallocation(
        self,
        user_id: str,
        month: str
    ) -> List[dict]:
        """
        Suggest budget adjustments based on spending patterns
        e.g., "You're overspending on dining, reallocate from entertainment?"
        """
        pass
```

**API Endpoints:**
```
POST   /budget/create
POST   /budget/check-purchase
GET    /budget/summary?user_id={id}&month={YYYY-MM}
PUT    /budget/update-spent
GET    /budget/suggestions?user_id={id}&month={YYYY-MM}
```

**Example Request/Response:**
```json
POST /budget/check-purchase
{
    "user_id": "user_123",
    "amount": 200.00,
    "category_id": "cat_dining",
    "month": "2025-10"
}

Response:
{
    "fits_budget": false,
    "remaining_in_category": 50.00,
    "percentage_of_category": 133.3,
    "warning": "This exceeds your dining budget by $150",
    "alternative_options": [
        "Cook at home this week to save $100",
        "Postpone until next month when budget resets"
    ]
}
```

---

### 4. AI Layer (LLM Service)

```python
class AIService:
    """LLM-powered reasoning and recommendations"""

    async def chat(
        self,
        user_id: str,
        message: str,
        context: dict
    ) -> ChatMessage:
        """
        Main chat interface
        Handles: expense logging, purchase questions, budget queries
        Context includes: current budget, recent expenses, goals
        """
        pass

    async def analyze_purchase(
        self,
        user_id: str,
        item_description: str,
        amount: Decimal
    ) -> PurchaseRecommendation:
        """
        Generate buy/wait/don't buy recommendation
        Flow:
        1. Extract expense details from description
        2. Classify category (via Ranking System)
        3. Check budget (via Budget Engine)
        4. Apply reasoning (necessity, timing, alternatives)
        5. Return recommendation with explanation
        """
        pass

    async def extract_expense_from_text(
        self,
        text: str
    ) -> Expense:
        """
        Parse natural language into structured expense
        Example: "Spent $50 on gas yesterday" → Expense object
        """
        pass

    async def generate_budget_insights(
        self,
        user_id: str,
        month: str
    ) -> str:
        """
        Natural language budget summary
        Example: "You're on track! You've saved 15% more than last month..."
        """
        pass

    async def voice_to_text(self, audio_data: bytes) -> str:
        """Convert voice input to text (Whisper API)"""
        pass

    async def text_to_voice(self, text: str) -> bytes:
        """Convert response to speech (TTS)"""
        pass
```

**API Endpoints:**
```
POST   /ai/chat
POST   /ai/analyze-purchase
POST   /ai/extract-expense
GET    /ai/insights?user_id={id}&month={YYYY-MM}
POST   /ai/voice-to-text
POST   /ai/text-to-voice
```

**Example Request/Response:**
```json
POST /ai/analyze-purchase
{
    "user_id": "user_123",
    "item_description": "New iPhone 15 Pro",
    "amount": 1199.00
}

Response:
{
    "decision": "wait",
    "reason": "This purchase would consume 40% of your monthly budget and you have an iPhone 12 that's still functional. Your goal is to save for a house down payment.",
    "alternative_suggestions": [
        "Wait for iPhone 16 release when prices drop",
        "Consider certified refurbished iPhone 14 Pro ($799)",
        "Delay until next quarter when you get your bonus"
    ],
    "impact_on_budget": "Would leave only $800 for remaining categories this month",
    "category": "Electronics",
    "amount": 1199.00
}
```

---

### 5. Expense Service (Can be part of Budget Engine)

```python
class ExpenseService:
    """Manages expense tracking and history"""

    async def log_expense(
        self,
        user_id: str,
        expense: Expense
    ) -> Expense:
        """
        Record expense and update budget
        Triggers: Budget Engine update_spent_amount
        """
        pass

    async def get_expenses(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
        category_id: Optional[str] = None
    ) -> List[Expense]:
        """Fetch expense history with filters"""
        pass

    async def get_spending_patterns(
        self,
        user_id: str,
        months: int = 6
    ) -> dict:
        """
        Analyze spending trends
        Returns: Category-wise averages, spikes, patterns
        """
        pass
```

---

## Implementation Roadmap

### Phase 1: Foundation (Hours 0-6)
**Goal: Basic infrastructure and auth**

1. **Setup (Hour 0-1)**
   - Initialize monorepo or microservices structure
   - Setup Supabase project
   - Configure FastAPI services with Docker Compose
   - Setup API Gateway (simple FastAPI router for MVP)

2. **Auth Service (Hour 1-3)**
   - Implement Supabase Auth integration
   - JWT validation middleware
   - User registration/login endpoints
   - Basic user profile management

3. **Database Schema (Hour 3-4)**
   - Create all Supabase tables
   - Seed default categories
   - Setup RLS policies
   - Create database indexes

4. **Basic Frontend (Hour 4-6)**
   - Next.js setup with shadcn/ui
   - Auth pages (login/register)
   - Protected route wrapper
   - Basic chat interface layout

### Phase 2: Core Logic (Hours 6-14)
**Goal: Budget and ranking systems**

5. **Ranking System (Hour 6-8)**
   - Category classification logic
   - Priority calculation algorithm
   - User preference overrides
   - API endpoints

6. **Budget Engine (Hour 8-11)**
   - Budget creation algorithm
   - Allocation logic (50/30/20 rule + customization)
   - Purchase validation
   - Spent amount tracking

7. **Expense Management (Hour 11-12)**
   - Expense CRUD operations
   - Automatic budget updates
   - Spending pattern analysis

8. **Frontend - Budget Views (Hour 12-14)**
   - Budget creation form
   - Budget dashboard with charts
   - Category allocation editor
   - Expense list with filters

### Phase 3: AI Integration (Hours 14-20)
**Goal: Intelligent recommendations**

9. **AI Service Setup (Hour 14-15)**
   - LangChain/OpenAI integration
   - Prompt engineering for categorization
   - Context building utilities

10. **Expense Classification (Hour 15-16)**
    - AI-powered category detection
    - Confidence scoring
    - Fallback to manual selection

11. **Purchase Recommendations (Hour 16-18)**
    - Implement decision logic
    - Generate explanations
    - Alternative suggestions
    - Integration with Budget Engine

12. **Chat Interface (Hour 18-20)**
    - Natural language expense parsing
    - Conversational budget queries
    - Chat history persistence
    - Frontend chat UI completion

### Phase 4: Polish & Features (Hours 20-24)
**Goal: Voice, UX, and testing**

13. **Voice Integration (Hour 20-21)**
    - Web Speech API for voice input
    - Whisper API for transcription
    - TTS for responses
    - Voice UI components

14. **UX Refinement (Hour 21-22)**
    - Loading states
    - Error handling
    - Responsive design
    - Animations and transitions

15. **Testing & Bug Fixes (Hour 22-23)**
    - Integration testing
    - Edge case handling
    - Performance optimization
    - Security review

16. **Demo Preparation (Hour 23-24)**
    - Seed demo data
    - Prepare demo script
    - Deploy to production (Vercel + Railway/Fly.io)
    - Create pitch deck

---

## Best Practices & Scaling

### 1. Service Communication

**For MVP (24-hour hackathon):**
```python
# Direct HTTP calls with httpx
async def check_budget_before_ai_response():
    async with httpx.AsyncClient() as client:
        budget_response = await client.post(
            "http://budget-engine:8001/check-purchase",
            json={"user_id": user_id, "amount": amount, "category_id": cat_id}
        )
    return budget_response.json()
```

**For Production (future):**
- **Event-Driven**: Use Redis Pub/Sub or RabbitMQ for async events
  - `expense.created` → Update budget
  - `budget.exceeded` → Trigger notification
- **Service Mesh**: Istio/Linkerd for observability
- **API Versioning**: `/v1/budget/`, `/v2/budget/`

### 2. Async Communication Pattern

```python
# Example: Event-driven expense logging
from fastapi import BackgroundTasks

@app.post("/expenses/log")
async def log_expense(expense: Expense, background_tasks: BackgroundTasks):
    # Immediate response
    saved_expense = await db.save_expense(expense)

    # Background tasks (non-blocking)
    background_tasks.add_task(update_budget_spent, expense)
    background_tasks.add_task(check_budget_alerts, expense.user_id)
    background_tasks.add_task(log_analytics_event, expense)

    return saved_expense
```

### 3. Caching Strategy

```python
from functools import lru_cache
import redis

# In-memory cache for categories (rarely change)
@lru_cache(maxsize=100)
async def get_system_categories():
    return await db.fetch_categories()

# Redis for user-specific data
redis_client = redis.Redis(host='localhost', port=6379)

async def get_user_budget(user_id: str, month: str):
    cache_key = f"budget:{user_id}:{month}"
    cached = redis_client.get(cache_key)

    if cached:
        return json.loads(cached)

    budget = await db.get_budget(user_id, month)
    redis_client.setex(cache_key, 3600, json.dumps(budget))  # 1hr TTL
    return budget
```

### 4. Error Handling & Resilience

```python
from tenacity import retry, stop_after_attempt, wait_exponential

class ServiceError(Exception):
    pass

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def call_ai_service(prompt: str):
    try:
        response = await ai_client.complete(prompt)
        return response
    except Exception as e:
        logger.error(f"AI service error: {e}")
        raise ServiceError("AI temporarily unavailable")

# Graceful degradation
async def get_purchase_recommendation(item: str, amount: Decimal):
    try:
        return await call_ai_service(f"Should I buy {item} for ${amount}?")
    except ServiceError:
        # Fallback to rule-based system
        return rule_based_recommendation(item, amount)
```

### 5. Database Optimization

```sql
-- Indexes for common queries
CREATE INDEX idx_expenses_user_date ON expenses(user_id, date DESC);
CREATE INDEX idx_expenses_category ON expenses(category_id);
CREATE INDEX idx_budget_user_month ON budgets(user_id, month);

-- Materialized view for spending summaries
CREATE MATERIALIZED VIEW monthly_spending_summary AS
SELECT
    user_id,
    category_id,
    DATE_TRUNC('month', date) as month,
    SUM(amount) as total_spent,
    COUNT(*) as transaction_count
FROM expenses
GROUP BY user_id, category_id, DATE_TRUNC('month', date);

-- Refresh periodically
REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_spending_summary;
```

### 6. Security Best Practices

```python
# Rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/ai/chat")
@limiter.limit("10/minute")  # Prevent AI abuse
async def chat_endpoint(message: str, user: User = Depends(get_current_user)):
    pass

# Input validation
from pydantic import validator, constr

class ExpenseInput(BaseModel):
    description: constr(max_length=500)
    amount: Decimal

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        if v > Decimal('1000000'):
            raise ValueError('Amount exceeds maximum')
        return v

# Secure environment variables
from pydantic import BaseSettings

class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    openai_api_key: str

    class Config:
        env_file = '.env'
        case_sensitive = False
```

### 7. Observability

```python
import structlog
from opentelemetry import trace

logger = structlog.get_logger()
tracer = trace.get_tracer(__name__)

async def create_budget(user_id: str, month: str):
    with tracer.start_as_current_span("create_budget") as span:
        span.set_attribute("user_id", user_id)
        span.set_attribute("month", month)

        logger.info("budget_creation_started", user_id=user_id, month=month)

        try:
            budget = await budget_engine.generate(user_id, month)
            logger.info("budget_created", budget_id=budget.id)
            return budget
        except Exception as e:
            logger.error("budget_creation_failed", error=str(e))
            span.record_exception(e)
            raise
```

### 8. Deployment Architecture (Post-Hackathon)

```yaml
# docker-compose.yml (for local dev)
version: '3.8'
services:
  api-gateway:
    build: ./gateway
    ports: ["8000:8000"]
    depends_on: [auth-service, budget-engine, ai-service]

  auth-service:
    build: ./services/auth
    environment:
      - SUPABASE_URL=${SUPABASE_URL}

  budget-engine:
    build: ./services/budget
    deploy:
      replicas: 2  # Horizontal scaling

  ai-service:
    build: ./services/ai
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G

  redis:
    image: redis:7-alpine

  postgres:
    image: postgres:15
    volumes:
      - pgdata:/var/lib/postgresql/data
```

**Production Deployment Options:**
- **Frontend**: Vercel/Netlify
- **Services**: Railway, Fly.io, or AWS ECS
- **Database**: Supabase (managed Postgres)
- **AI**: OpenAI API / Anthropic Claude API
- **Monitoring**: Sentry + Datadog/Grafana

---

## Quick Start Commands

```bash
# Setup
git clone <repo>
cd budgetwise
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Environment
cp .env.example .env
# Fill in: SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY

# Database
supabase db push  # Apply migrations

# Run services (local)
docker-compose up

# Or run individually:
uvicorn services.auth.main:app --port 8001 --reload
uvicorn services.budget.main:app --port 8002 --reload
uvicorn services.ai.main:app --port 8003 --reload

# Frontend
cd frontend
npm install
npm run dev
```

---

## API Flow Examples

### Complete Purchase Decision Flow

```
1. User asks: "Should I buy a $500 PlayStation 5?"

2. Frontend → AI Service POST /ai/chat
   {
     "user_id": "user_123",
     "message": "Should I buy a $500 PlayStation 5?"
   }

3. AI Service extracts:
   - Item: "PlayStation 5"
   - Amount: $500
   - Intent: Purchase decision

4. AI Service → Ranking System POST /ranking/classify
   {
     "description": "PlayStation 5",
     "amount": 500,
     "user_id": "user_123"
   }

   Response: { "category": "Entertainment", "necessity_score": 3 }

5. AI Service → Budget Engine POST /budget/check-purchase
   {
     "user_id": "user_123",
     "amount": 500,
     "category_id": "cat_entertainment",
     "month": "2025-10"
   }

   Response: {
     "fits_budget": false,
     "remaining_in_category": 100,
     "percentage_of_category": 500%
   }

6. AI Service generates recommendation:
   - Decision: "don't_buy"
   - Reason: Exceeds entertainment budget by 400%
   - Alternatives: Wait for Black Friday, use savings from other categories

7. Response → Frontend
   {
     "decision": "don't_buy",
     "reason": "...",
     "alternatives": [...]
   }
```

---

## File Structure

```
budgetwise/
├── services/
│   ├── auth/
│   │   ├── main.py
│   │   ├── models.py
│   │   └── routes.py
│   ├── budget/
│   │   ├── main.py
│   │   ├── engine.py
│   │   └── routes.py
│   ├── ranking/
│   │   ├── main.py
│   │   ├── classifier.py
│   │   └── routes.py
│   └── ai/
│       ├── main.py
│       ├── llm.py
│       ├── prompts.py
│       └── routes.py
├── shared/
│   ├── models.py (Pydantic models)
│   ├── database.py (Supabase client)
│   └── utils.py
├── frontend/
│   ├── app/
│   │   ├── (auth)/
│   │   ├── dashboard/
│   │   └── chat/
│   ├── components/
│   └── lib/
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

**This architecture supports:**
- ✅ Clean separation of concerns
- ✅ Independent service scaling
- ✅ Easy testing (mock service boundaries)
- ✅ Rapid MVP development
- ✅ Production-ready foundations

Ready to build! 🚀