"""
API Routes for AI Pipeline Service
"""

import sys
from pathlib import Path

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from fastapi import APIRouter, HTTPException, status, UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from ai_service import ai_service
from orchestrator import orchestrator
from voice_service import voice_service, whisper_stt, voice_chat_pipeline
from shared.database import db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Pipeline"])


# ============= Request/Response Models =============

class ChatRequest(BaseModel):
    user_id: str
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    metadata: Optional[Dict[str, Any]] = None


class PurchaseAnalysisRequest(BaseModel):
    user_id: str
    item: str
    amount: float = Field(..., gt=0)
    user_message: Optional[str] = None


class PurchaseAnalysisResponse(BaseModel):
    decision: str  # buy, wait, dont_buy
    reason: str
    alternatives: List[str] = []
    impact: str
    confidence: float
    category: Optional[str] = None
    budget_remaining: Optional[float] = None


class ExpenseExtractionRequest(BaseModel):
    message: str
    user_id: str


class ExpenseExtractionResponse(BaseModel):
    amount: Optional[float]
    description: str
    merchant: Optional[str]
    date: Optional[str]
    item: Optional[str]
    category: Optional[str] = None
    category_confidence: Optional[float] = None


class BudgetInsightsResponse(BaseModel):
    insights: str
    total_budget: float
    total_spent: float
    total_remaining: float
    month: str


class ClassifyExpenseRequest(BaseModel):
    user_id: str
    description: str
    amount: float = Field(..., gt=0)
    merchant: Optional[str] = None


class ClassifyExpenseResponse(BaseModel):
    category_id: str
    category_name: str
    necessity_score: int
    confidence: float
    reasoning: Optional[str] = None


# ============= Chat Endpoint =============

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main conversational AI endpoint with function calling support

    Handles:
    - Budget creation
    - Expense logging
    - Purchase analysis
    - General budget questions
    - Financial guidance
    """
    try:
        # Get conversation history
        conversation_history = []
        if request.conversation_id:
            history = db.get_conversation_history(
                request.conversation_id,
                limit=10
            )
            conversation_history = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in history
            ]

        # Get user context
        user_context = await orchestrator.get_user_context(request.user_id)

        # Call AI with function calling enabled
        ai_response = await ai_service.chat_with_functions(
            user_message=request.message,
            user_id=request.user_id,
            conversation_history=conversation_history,
            context={
                "budget_status": user_context.get("budget_summary", {}),
                "recent_expenses": []  # TODO: Fetch from DB
            }
        )

        # Initialize response message
        response_message = ai_response["message"]
        metadata = {"user_context": user_context}

        # If AI wants to call a function, execute it
        if ai_response["requires_function"]:
            function_name = ai_response["function_name"]
            function_args = ai_response["function_args"]

            logger.info(f"Executing function: {function_name} with args: {function_args}")

            try:
                # Execute the appropriate function
                function_result = await execute_function(function_name, function_args)

                # Generate natural language response based on function result
                response_message = await ai_service.generate_function_response(
                    user_message=request.message,
                    function_name=function_name,
                    function_result=function_result,
                    conversation_history=conversation_history
                )

                # Add function result to metadata
                metadata["function_executed"] = function_name
                metadata["function_result"] = function_result

            except Exception as e:
                logger.error(f"Function execution error: {e}")
                response_message = f"I tried to {function_name.replace('_', ' ')}, but encountered an error: {str(e)}"

        # Generate conversation ID if new
        conv_id = request.conversation_id or f"conv_{request.user_id}_{int(datetime.now().timestamp())}"

        # Save messages to database
        db.save_chat_message(
            user_id=request.user_id,
            role="user",
            content=request.message,
            conversation_id=conv_id
        )
        db.save_chat_message(
            user_id=request.user_id,
            role="assistant",
            content=response_message,
            conversation_id=conv_id,
            metadata=metadata if ai_response["requires_function"] else None
        )

        return ChatResponse(
            conversation_id=conv_id,
            message=response_message,
            metadata=metadata
        )

    except Exception as e:
        logger.error(f"Chat error ({type(e).__name__}): {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat processing failed: {str(e)}"
        )


async def execute_function(function_name: str, function_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a function called by the AI

    Args:
        function_name: Name of the function to execute
        function_args: Arguments for the function

    Returns:
        Function execution result
    """
    from datetime import datetime

    user_id = function_args.get("user_id")

    if function_name == "create_budget":
        # Create budget via orchestrator
        income = function_args.get("income")
        month = function_args.get("month", datetime.now().strftime("%Y-%m"))
        goals = function_args.get("goals", [])

        result = await orchestrator.create_budget(
            user_id=user_id,
            month=month,
            income=float(income),
            goals=goals
        )
        return result

    elif function_name == "log_expense":
        # Log expense and update budget
        description = function_args.get("description")
        amount = function_args.get("amount")
        merchant = function_args.get("merchant")
        date = function_args.get("date", "today")

        # Use orchestrator's log_expense_workflow
        result = await orchestrator.log_expense_workflow(
            user_id=user_id,
            description=description,
            amount=float(amount),
            date=date
        )

        # Also save to expenses table
        expense_data = {
            "user_id": user_id,
            "amount": str(amount),
            "description": description,
            "category_id": result.get("category_id"),
            "date": datetime.now().isoformat(),
            "ai_suggested_category": result.get("category_id"),
            "confidence_score": str(result.get("confidence", 0))
        }
        db.save_expense(expense_data)

        return result

    elif function_name == "analyze_purchase":
        # Analyze purchase decision
        item = function_args.get("item")
        amount = function_args.get("amount")

        # Get user profile for analysis
        user = db.get_user(user_id)
        user_profile = {
            "monthly_income": float(user.get("monthly_income", 0)) if user else 0,
            "financial_goals": user.get("financial_goals", []) if user else [],
            "risk_tolerance": user.get("risk_tolerance", "moderate") if user else "moderate"
        }

        # Use orchestrator to get purchase context
        context = await orchestrator.analyze_purchase_decision(
            user_id=user_id,
            user_message=f"Should I buy {item}?",
            item=item,
            amount=float(amount)
        )

        # Get AI recommendation
        recommendation = await ai_service.analyze_purchase(
            user_message=f"Should I buy {item}?",
            item=item,
            amount=float(amount),
            category=context["category"],
            necessity_score=context["necessity_score"],
            budget_context=context["budget_context"],
            user_profile=user_profile
        )

        return recommendation

    elif function_name == "get_budget_summary":
        # Get budget summary
        month = function_args.get("month", datetime.now().strftime("%Y-%m"))
        result = await orchestrator.get_budget_summary(user_id, month)
        return result

    elif function_name == "get_budget_insights":
        # Get AI-generated insights
        month = function_args.get("month", datetime.now().strftime("%Y-%m"))
        budget_summary = await orchestrator.get_budget_summary(user_id, month)

        insights = await ai_service.generate_budget_insights(
            budget_summary=budget_summary,
            month=month,
            spending_patterns=None
        )

        return {"insights": insights, "month": month}

    else:
        raise ValueError(f"Unknown function: {function_name}")


# ============= Purchase Analysis =============

@router.post("/analyze-purchase", response_model=PurchaseAnalysisResponse)
async def analyze_purchase(request: PurchaseAnalysisRequest):
    """
    Analyze a purchase decision with AI

    Flow:
    1. Classify item category (Ranking System)
    2. Check budget availability (Budget Engine)
    3. Get user profile
    4. Generate AI recommendation
    """
    try:
        # Get user profile
        user = await db.get_user(request.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Orchestrate purchase analysis
        context = await orchestrator.analyze_purchase_decision(
            user_id=request.user_id,
            user_message=request.user_message or f"Should I buy {request.item}?",
            item=request.item,
            amount=request.amount
        )

        # Prepare user profile
        user_profile = {
            "monthly_income": float(user.get("monthly_income", 0)),
            "financial_goals": user.get("financial_goals", []),
            "risk_tolerance": user.get("risk_tolerance", "moderate")
        }

        # Get AI recommendation
        recommendation = await ai_service.analyze_purchase(
            user_message=context["user_message"],
            item=context["item"],
            amount=context["amount"],
            category=context["category"],
            necessity_score=context["necessity_score"],
            budget_context=context["budget_context"],
            user_profile=user_profile
        )

        return PurchaseAnalysisResponse(
            decision=recommendation.get("decision", "wait"),
            reason=recommendation.get("reason", "Unable to generate recommendation"),
            alternatives=recommendation.get("alternatives", []),
            impact=recommendation.get("impact", "Unknown impact"),
            confidence=recommendation.get("confidence", 0.5),
            category=context["category"],
            budget_remaining=context["budget_context"].get("remaining_amount", 0)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Purchase analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Purchase analysis failed: {str(e)}"
        )


# ============= Expense Extraction =============

@router.post("/extract-expense", response_model=ExpenseExtractionResponse)
async def extract_expense(request: ExpenseExtractionRequest):
    """
    Extract structured expense data from natural language

    Example: "I spent $50 on gas yesterday"
    Returns: {amount: 50, description: "gas", date: "yesterday", ...}
    """
    try:
        # Extract expense details
        extracted = await ai_service.extract_expense(request.message)

        # If amount was extracted, classify the category
        category = None
        category_confidence = None

        if extracted.get("amount") and extracted.get("description"):
            classification = await orchestrator.classify_expense(
                description=extracted["description"],
                amount=extracted["amount"],
                user_id=request.user_id
            )
            category = classification.get("category", {}).get("name")
            category_confidence = classification.get("confidence")

        return ExpenseExtractionResponse(
            amount=extracted.get("amount"),
            description=extracted.get("description", request.message),
            merchant=extracted.get("merchant"),
            date=extracted.get("date"),
            item=extracted.get("item"),
            category=category,
            category_confidence=category_confidence
        )

    except Exception as e:
        logger.error(f"Expense extraction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Expense extraction failed: {str(e)}"
        )


# ============= Expense Classification =============

@router.post("/classify-expense", response_model=ClassifyExpenseResponse)
async def classify_expense(request: ClassifyExpenseRequest):
    """
    AI-powered expense classification using GPT-4o-mini

    Intelligently categorizes expenses based on merchant and description,
    returning high-confidence classifications (0.80-0.95 expected).

    This uses the AI Service, NOT semantic embeddings.
    """
    try:
        # Call orchestrator's classify_expense which uses AI Service
        classification = await orchestrator.classify_expense(
            description=request.description,
            amount=request.amount,
            user_id=request.user_id,
            merchant=request.merchant
        )

        return ClassifyExpenseResponse(
            category_id=classification.get("category_id", "unknown"),
            category_name=classification.get("category_name", "Uncategorized"),
            necessity_score=classification.get("necessity_score", 5),
            confidence=classification.get("confidence", 0.0),
            reasoning=classification.get("reasoning")
        )

    except Exception as e:
        logger.error(f"Expense classification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Expense classification failed: {str(e)}"
        )


# ============= Budget Insights =============

@router.get("/insights", response_model=BudgetInsightsResponse)
async def get_budget_insights(
    user_id: str,
    month: Optional[str] = None
):
    """
    Generate natural language budget insights and recommendations

    Returns personalized financial advice based on spending patterns
    """
    try:
        if not month:
            month = datetime.now().strftime("%Y-%m")

        # Get budget summary
        budget_summary = await orchestrator.get_budget_summary(user_id, month)

        # Get spending patterns (future: from vector store)
        spending_patterns = None  # TODO: Implement pattern analysis

        # Generate insights
        insights_text = await ai_service.generate_budget_insights(
            budget_summary=budget_summary,
            month=month,
            spending_patterns=spending_patterns
        )

        return BudgetInsightsResponse(
            insights=insights_text,
            total_budget=budget_summary.get("total_budget", 0),
            total_spent=budget_summary.get("total_spent", 0),
            total_remaining=budget_summary.get("total_remaining", 0),
            month=month
        )

    except Exception as e:
        logger.error(f"Budget insights error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Insights generation failed: {str(e)}"
        )


# ============= Voice Endpoints (Ready but dormant) =============

@router.post("/voice-to-text")
async def voice_to_text(audio: UploadFile = File(...)):
    """
    Convert voice input to text using Whisper

    Currently dormant until backend is stable
    """
    try:
        if not whisper_stt.enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Voice-to-text service not enabled"
            )

        # Read audio data
        audio_data = await audio.read()

        # Transcribe
        transcription = await whisper_stt.transcribe(audio_data)

        if not transcription:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Transcription failed"
            )

        return {"text": transcription}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice-to-text error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Voice-to-text failed: {str(e)}"
        )


@router.post("/text-to-voice")
async def text_to_voice(text: str, voice_id: Optional[str] = None):
    """
    Convert text to speech using ElevenLabs

    Currently dormant until backend is stable
    """
    try:
        if not voice_service.enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Text-to-voice service not enabled"
            )

        # Generate speech
        audio_bytes = await voice_service.text_to_speech(text, voice_id)

        if not audio_bytes:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Speech generation failed"
            )

        # Return audio file
        from fastapi.responses import Response
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=speech.mp3"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text-to-voice error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text-to-voice failed: {str(e)}"
        )


@router.post("/voice-chat")
async def voice_chat(audio: UploadFile = File(...)):
    """
    Complete voice interaction pipeline:
    1. Convert speech to text
    2. Process with AI
    3. Convert response to speech

    Currently dormant until backend is stable
    """
    try:
        if not (whisper_stt.enabled and voice_service.enabled):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Voice chat service not fully enabled"
            )

        audio_data = await audio.read()
        result = await voice_chat_pipeline(audio_data)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Voice chat pipeline failed"
            )

        # Return both text and audio
        from fastapi.responses import Response
        return {
            "transcribed_text": result["transcribed_text"],
            "ai_response_text": result["ai_response_text"],
            "audio_available": result["response_audio"] is not None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Voice chat failed: {str(e)}"
        )


# ============= Health & Info =============

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ai_service": "enabled",
        "voice_service": "dormant" if not voice_service.enabled else "enabled",
        "vector_store": "skeleton"
    }
