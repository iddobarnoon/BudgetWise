"""
OpenAI GPT-4o-mini integration for BudgetWise AI
"""

import os
import json
from typing import Optional, Dict, Any, List
from pathlib import Path
from dotenv import load_dotenv
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

# Load environment variables
env_path = Path(__file__).resolve().parent.parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from prompts import (
    FINANCIAL_ADVISOR_SYSTEM_PROMPT,
    format_purchase_analysis_prompt,
    format_expense_extraction_prompt,
    format_budget_insights_prompt,
    format_chat_prompt,
    format_category_classification_prompt
)

logger = logging.getLogger(__name__)


class AIService:
    """OpenAI-powered AI service for financial recommendations"""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable must be set")

        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"
        self.temperature = 0.7
        self.max_tokens = 1000

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _call_openai(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Call OpenAI API with retry logic

        Args:
            system_prompt: System message for the AI
            user_prompt: User message/prompt
            temperature: Override default temperature
            max_tokens: Override default max tokens
            response_format: Optional format specification (e.g., {"type": "json_object"})

        Returns:
            AI response content
        """
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature or self.temperature,
                "max_tokens": max_tokens or self.max_tokens
            }

            if response_format:
                kwargs["response_format"] = response_format

            response = await self.client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content

            logger.info(f"OpenAI API call successful. Tokens used: {response.usage.total_tokens}")
            return content

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

    async def analyze_purchase(
        self,
        user_message: str,
        item: str,
        amount: float,
        category: str,
        necessity_score: int,
        budget_context: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze a purchase decision

        Args:
            user_message: Original user question
            item: Item being considered
            amount: Purchase amount
            category: Classified category
            necessity_score: Category necessity score (1-10)
            budget_context: Budget information
            user_profile: User financial profile

        Returns:
            Purchase recommendation with decision, reason, alternatives
        """
        prompt = format_purchase_analysis_prompt(
            user_message=user_message,
            item=item,
            amount=amount,
            category=category,
            necessity_score=necessity_score,
            category_budget=budget_context.get("category_budget", 0),
            spent_amount=budget_context.get("spent_amount", 0),
            remaining_amount=budget_context.get("remaining_amount", 0),
            fits_budget=budget_context.get("fits_budget", False),
            monthly_income=user_profile.get("monthly_income", 0),
            financial_goals=user_profile.get("financial_goals", []),
            risk_tolerance=user_profile.get("risk_tolerance", "moderate")
        )

        try:
            response_content = await self._call_openai(
                system_prompt=FINANCIAL_ADVISOR_SYSTEM_PROMPT,
                user_prompt=prompt,
                response_format={"type": "json_object"}
            )

            # Parse JSON response
            result = json.loads(response_content)
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            # Fallback to rule-based decision
            return self._fallback_purchase_decision(amount, budget_context)
        except Exception as e:
            logger.error(f"Purchase analysis error: {e}")
            return self._fallback_purchase_decision(amount, budget_context)

    async def extract_expense(self, message: str) -> Dict[str, Any]:
        """
        Extract expense details from natural language

        Args:
            message: User message (e.g., "I spent $50 on gas yesterday")

        Returns:
            Extracted expense data (amount, description, merchant, date, item)
        """
        prompt = format_expense_extraction_prompt(message)

        try:
            response_content = await self._call_openai(
                system_prompt="You are an expert at extracting structured data from text.",
                user_prompt=prompt,
                response_format={"type": "json_object"},
                temperature=0.3  # Lower temperature for extraction
            )

            result = json.loads(response_content)
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse expense extraction: {e}")
            return {"amount": None, "description": message, "merchant": None, "date": "today", "item": None}
        except Exception as e:
            logger.error(f"Expense extraction error: {e}")
            return {"amount": None, "description": message, "merchant": None, "date": "today", "item": None}

    async def generate_budget_insights(
        self,
        budget_summary: Dict[str, Any],
        month: str,
        spending_patterns: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate natural language budget insights

        Args:
            budget_summary: Budget summary data
            month: Budget month
            spending_patterns: Historical spending patterns

        Returns:
            Natural language insights and recommendations
        """
        # Format category breakdown
        category_breakdown = "\n".join([
            f"- {cat['category_name']}: ${cat['spent']:.2f} / ${cat['allocated']:.2f}"
            for cat in budget_summary.get("categories", [])
        ])

        # Format overspent categories
        overspent = budget_summary.get("overspent_categories", [])
        overspent_text = ", ".join(overspent) if overspent else "None"

        # Format spending patterns
        patterns_text = "No historical data available"
        if spending_patterns:
            patterns_text = json.dumps(spending_patterns, indent=2)

        prompt = format_budget_insights_prompt(
            total_budget=budget_summary.get("total_budget", 0),
            total_spent=budget_summary.get("total_spent", 0),
            total_remaining=budget_summary.get("total_remaining", 0),
            month=month,
            category_breakdown=category_breakdown,
            spending_patterns=patterns_text,
            overspent_categories=overspent_text
        )

        try:
            response = await self._call_openai(
                system_prompt=FINANCIAL_ADVISOR_SYSTEM_PROMPT,
                user_prompt=prompt
            )
            return response

        except Exception as e:
            logger.error(f"Budget insights error: {e}")
            return self._fallback_budget_insights(budget_summary)

    async def chat(
        self,
        user_message: str,
        user_id: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Handle conversational chat with context

        Args:
            user_message: User's message
            user_id: User ID
            conversation_history: Previous messages
            context: Additional context (budget status, recent expenses)

        Returns:
            AI response
        """
        # Format conversation history
        history_text = ""
        if conversation_history:
            history_text = "\n".join([
                f"{msg['role'].capitalize()}: {msg['content']}"
                for msg in conversation_history[-5:]  # Last 5 messages
            ])

        # Format context
        budget_status = "Not available"
        recent_expenses = "None"
        if context:
            budget_status = json.dumps(context.get("budget_status", {}), indent=2)
            recent_expenses = json.dumps(context.get("recent_expenses", []), indent=2)

        prompt = format_chat_prompt(
            conversation_history=history_text or "No previous conversation",
            user_message=user_message,
            user_id=user_id,
            budget_status=budget_status,
            recent_expenses=recent_expenses
        )

        try:
            response = await self._call_openai(
                system_prompt=FINANCIAL_ADVISOR_SYSTEM_PROMPT,
                user_prompt=prompt
            )
            return response

        except Exception as e:
            logger.error(f"Chat error: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again."

    async def classify_category(
        self,
        description: str,
        amount: float,
        categories: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Classify expense into a category using AI

        Args:
            description: Expense description
            amount: Expense amount
            categories: Available categories

        Returns:
            Category classification with confidence
        """
        # Format categories for prompt
        categories_text = "\n".join([
            f"- {cat['name']} (ID: {cat['id']}, Necessity: {cat.get('necessity_score', 'N/A')})"
            for cat in categories
        ])

        prompt = format_category_classification_prompt(
            description=description,
            amount=amount,
            categories=categories_text
        )

        try:
            response_content = await self._call_openai(
                system_prompt="You are an expert at categorizing expenses.",
                user_prompt=prompt,
                response_format={"type": "json_object"},
                temperature=0.3
            )

            result = json.loads(response_content)
            return result

        except Exception as e:
            logger.error(f"Category classification error: {e}")
            return {
                "category_id": categories[0]["id"] if categories else None,
                "category_name": categories[0]["name"] if categories else "Unknown",
                "confidence": 0.5,
                "reasoning": "Fallback to default category"
            }

    def _fallback_purchase_decision(
        self,
        amount: float,
        budget_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback rule-based purchase decision"""
        remaining = budget_context.get("remaining_amount", 0)
        fits_budget = budget_context.get("fits_budget", False)

        if not fits_budget:
            return {
                "decision": "dont_buy",
                "reason": "This purchase exceeds your remaining budget for this category.",
                "alternatives": ["Wait until next month", "Look for a more affordable option"],
                "impact": f"Would exceed budget by ${amount - remaining:.2f}",
                "confidence": 0.9
            }
        elif remaining - amount < 50:
            return {
                "decision": "wait",
                "reason": "This purchase would leave you with very little budget remaining.",
                "alternatives": ["Consider if this is essential", "Delay until mid-month"],
                "impact": f"Would leave only ${remaining - amount:.2f} remaining",
                "confidence": 0.8
            }
        else:
            return {
                "decision": "buy",
                "reason": "This purchase fits comfortably within your budget.",
                "alternatives": [],
                "impact": f"Would leave ${remaining - amount:.2f} remaining",
                "confidence": 0.7
            }

    def _fallback_budget_insights(self, budget_summary: Dict[str, Any]) -> str:
        """Fallback budget insights"""
        total_budget = budget_summary.get("total_budget", 0)
        total_spent = budget_summary.get("total_spent", 0)
        total_remaining = budget_summary.get("total_remaining", 0)
        percent_spent = (total_spent / total_budget * 100) if total_budget > 0 else 0

        return f"""
Budget Overview:
- You've spent ${total_spent:.2f} out of ${total_budget:.2f} ({percent_spent:.1f}%)
- Remaining: ${total_remaining:.2f}

{'⚠️ You are overspending in some categories. Review your budget and adjust spending.' if total_spent > total_budget else '✅ You are on track with your budget.'}
"""


# Global AI service instance
ai_service = AIService()
