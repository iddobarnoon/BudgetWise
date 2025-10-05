# BudgetWise AI Pipeline Service 🤖

AI-powered financial advisory service using OpenAI GPT-4o-mini, with voice capabilities via ElevenLabs and Whisper.

## 🚀 Features

### Active Features
- ✅ **Conversational AI Chat** - Natural language budget conversations
- ✅ **Purchase Recommendations** - Smart buy/wait/don't buy decisions
- ✅ **Expense Parsing** - Extract structured data from text like "I spent $50 on gas"
- ✅ **Budget Insights** - Personalized financial advice and summaries

### Setup But Dormant (Until Backend Stable)
- ⏸️ **Voice-to-Text** - Whisper API integration
- ⏸️ **Text-to-Voice** - ElevenLabs TTS
- ⏸️ **Voice Chat Pipeline** - Complete voice interaction

### Future Ready
- 📦 **Vector Store Skeleton** - Ready for embedding-based RAG
- 🧠 **Contextual Retrieval** - User history and knowledge base search

## 📋 Architecture

```
pipeline/
├── app.py              # FastAPI application
├── routes.py           # API endpoints
├── ai_service.py       # OpenAI GPT-4o-mini integration
├── orchestrator.py     # Service coordination (Budget + Ranking)
├── prompts.py          # LLM prompt templates
├── voice_service.py    # ElevenLabs + Whisper (dormant)
├── vector_store.py     # Vector DB skeleton
└── main.py            # Entry point
```

## 🔧 Setup

### 1. Install Dependencies

```bash
# From project root
pip install -e .
# or
poetry install
```

### 2. Configure Environment Variables

Add to your `.env` file:

```bash
# OpenAI (Required)
OPENAI_API_KEY=your_openai_api_key_here

# ElevenLabs (Optional - for voice features)
ELEVENLABS_API_KEY=sk_61322e7a89732c756005100ef9dc9e252e698711e0f252ae
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# Service URLs
BUDGET_ENGINE_URL=http://localhost:8003
RANKING_SERVICE_URL=http://localhost:8002
```

### 3. Start the Service

```bash
# From pipeline directory
cd src/backend/components/pipeline
python main.py
```

The service will start on **http://localhost:8004**

## 📡 API Endpoints

### Chat Interface
```bash
POST /ai/chat
{
  "user_id": "user_123",
  "message": "How much have I spent this month?",
  "conversation_id": "optional_conv_id"
}
```

### Purchase Analysis
```bash
POST /ai/analyze-purchase
{
  "user_id": "user_123",
  "item": "PlayStation 5",
  "amount": 500.00,
  "user_message": "Should I buy this?"
}
```

**Response:**
```json
{
  "decision": "wait",
  "reason": "This would consume 40% of your monthly budget...",
  "alternatives": [
    "Wait for Black Friday sales",
    "Consider PS4 Pro as alternative"
  ],
  "impact": "Would leave only $750 remaining",
  "confidence": 0.85,
  "category": "Entertainment",
  "budget_remaining": 750.00
}
```

### Expense Extraction
```bash
POST /ai/extract-expense
{
  "user_id": "user_123",
  "message": "I spent $50 on gas yesterday at Shell"
}
```

**Response:**
```json
{
  "amount": 50.00,
  "description": "gas",
  "merchant": "Shell",
  "date": "yesterday",
  "item": "gas",
  "category": "Transportation",
  "category_confidence": 0.95
}
```

### Budget Insights
```bash
GET /ai/insights?user_id=user_123&month=2025-10
```

**Response:**
```json
{
  "insights": "Great job! You're 20% under budget this month. Your grocery spending is particularly efficient...",
  "total_budget": 3000.00,
  "total_spent": 2400.00,
  "total_remaining": 600.00,
  "month": "2025-10"
}
```

## 🔗 Service Integration

The AI Pipeline orchestrates calls to:

1. **Ranking System** (port 8002) - Category classification
2. **Budget Engine** (port 8003) - Budget validation
3. **Supabase** - User profiles and chat history

### Workflow Example: Purchase Decision

```
User → AI Pipeline
  ↓
1. Ranking System: Classify "PlayStation 5" → Entertainment (necessity: 3/10)
  ↓
2. Budget Engine: Check $500 against Entertainment budget
  ↓
3. GPT-4o-mini: Analyze with context → Generate recommendation
  ↓
User ← Decision + Reasoning + Alternatives
```

## 🧪 Testing

### Using cURL

```bash
# Test chat
curl -X POST http://localhost:8004/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "What is my budget status?"
  }'

# Test purchase analysis
curl -X POST http://localhost:8004/ai/analyze-purchase \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "item": "New laptop",
    "amount": 1200.00
  }'
```

### Using API Docs

Visit **http://localhost:8004/docs** for interactive Swagger UI

## 🎤 Voice Features (Dormant)

Voice features are configured but not active until backend is stable.

To enable:
1. Ensure `OPENAI_API_KEY` and `ELEVENLABS_API_KEY` are set
2. Voice endpoints will automatically activate

```bash
# Voice to text
POST /ai/voice-to-text
[Upload audio file]

# Text to voice
POST /ai/text-to-voice?text=Your budget looks great!

# Complete voice chat
POST /ai/voice-chat
[Upload audio question, receive audio response]
```

## 📊 AI Configuration

- **Model:** GPT-4o-mini
- **Temperature:** 0.7 (moderate creativity)
- **Max Tokens:** 1000
- **Retry Logic:** 3 attempts with exponential backoff
- **Persona:** Financial advisor - helpful, concise, budget-aware

## 🔮 Future Enhancements

### Vector Store / RAG
```python
# Planned implementation
from vector_store import vector_store, context_retriever

# Retrieve relevant past expenses
relevant = await context_retriever.get_relevant_expenses(
    user_id="user_123",
    query="Should I buy expensive groceries?",
    limit=5
)

# Augment AI prompt with user history
```

### Planned Vector DB Options
- **Pinecone** - Managed, easy setup
- **Weaviate** - Open source, feature-rich
- **Qdrant** - Fast, Python-native
- **ChromaDB** - Lightweight, local

## 🐛 Troubleshooting

### Service won't start
```bash
# Check if ports are available
netstat -an | grep 8004

# Verify dependencies
pip list | grep openai
pip list | grep elevenlabs
```

### OpenAI API errors
- Verify `OPENAI_API_KEY` is set correctly
- Check API quota: https://platform.openai.com/usage
- Review logs for specific error messages

### Service communication errors
- Ensure Budget Engine (8003) is running
- Ensure Ranking System (8002) is running
- Check firewall settings

## 📝 Logging

Logs include:
- API call successes/failures
- Token usage tracking
- Service integration status
- Error traces

View logs in console or configure file logging in `app.py`

## 🚢 Deployment

For production:
1. Set `ENVIRONMENT=production` in `.env`
2. Configure proper CORS origins in `app.py`
3. Use process manager (PM2, systemd)
4. Setup reverse proxy (Nginx)
5. Enable HTTPS

```bash
# Example with Gunicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8004
```

---

Built with ❤️ for BudgetWise Hackathon 🚀
