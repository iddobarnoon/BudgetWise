"""
BudgetWise AI Pipeline Service
Main FastAPI Application
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables FIRST
env_path = Path(__file__).parent.parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import logging

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="BudgetWise AI Pipeline",
    description="""
    AI-powered financial advisory service for BudgetWise

    Features:
    - 🤖 Conversational AI chat interface
    - 💡 Purchase decision recommendations
    - 📝 Natural language expense parsing
    - 📊 Budget insights and analytics
    - 🎤 Voice interaction (dormant until backend stable)
    - 🧠 Vector store ready for RAG (future)

    Powered by OpenAI GPT-4o-mini
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)

# Root endpoint
@app.get("/")
async def root():
    """Service information"""
    return {
        "service": "BudgetWise AI Pipeline",
        "status": "running",
        "version": "1.0.0",
        "ai_model": "gpt-4o-mini",
        "endpoints": {
            "chat": "POST /ai/chat",
            "purchase_analysis": "POST /ai/analyze-purchase",
            "expense_extraction": "POST /ai/extract-expense",
            "insights": "GET /ai/insights",
            "voice_to_text": "POST /ai/voice-to-text (dormant)",
            "text_to_voice": "POST /ai/text-to-voice (dormant)",
            "voice_chat": "POST /ai/voice-chat (dormant)"
        },
        "integrations": {
            "budget_engine": "http://localhost:8003",
            "ranking_system": "http://localhost:8002"
        },
        "features": {
            "conversational_ai": "enabled",
            "purchase_recommendations": "enabled",
            "expense_parsing": "enabled",
            "budget_insights": "enabled",
            "voice_interaction": "dormant",
            "vector_rag": "skeleton"
        }
    }

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-pipeline",
        "timestamp": "active"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    logger.info("="*70)
    logger.info("🤖 BudgetWise AI Pipeline Service Starting...")
    logger.info("="*70)
    logger.info("📍 Service URL: http://localhost:8004")
    logger.info("📖 API Docs: http://localhost:8004/docs")
    logger.info("🧠 AI Model: gpt-4o-mini (OpenAI)")
    logger.info("🔗 Budget Engine: http://localhost:8003")
    logger.info("🔗 Ranking System: http://localhost:8002")
    logger.info("="*70)
    logger.info("Features:")
    logger.info("  ✅ Chat Interface")
    logger.info("  ✅ Purchase Analysis")
    logger.info("  ✅ Expense Extraction")
    logger.info("  ✅ Budget Insights")
    logger.info("  ⏸️  Voice Features (dormant)")
    logger.info("  📦 Vector Store (skeleton)")
    logger.info("="*70)

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 AI Pipeline Service shutting down...")

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*70)
    print("🤖 Starting BudgetWise AI Pipeline Service...")
    print("="*70)
    print("📍 URL: http://localhost:8004")
    print("📖 Docs: http://localhost:8004/docs")
    print("🧠 AI: GPT-4o-mini")
    print("="*70 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8004, log_level="info")
