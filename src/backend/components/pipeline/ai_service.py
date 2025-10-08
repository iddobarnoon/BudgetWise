"""
OpenAI GPT-4o-mini integration for BudgetWise AI
"""

import os
import json
from typing import Optional, Dict, Any, List
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
from dotenv import load_dotenv

from prompts import (
    FINANCIAL_ADVISOR_SYSTEM_PROMPT,
    format_purchase_analysis_prompt,
    format_expense_extraction_prompt,
    format_budget_insights_prompt,
    format_chat_prompt,
    format_category_classification_prompt,
    OPENAI_FUNCTIONS
)
load_dotenv()
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
            f"- {cat['category_name']}: ${cat['spent_amount']:.2f} / ${cat['allocated_amount']:.2f}"
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

    async def chat_with_functions(
        self,
        user_message: str,
        user_id: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle conversational chat with function calling support

        Args:
            user_message: User's message
            user_id: User ID
            conversation_history: Previous messages
            context: Additional context (budget status, recent expenses)

        Returns:
            {
                "requires_function": bool,
                "function_name": str or None,
                "function_args": dict or None,
                "message": str (initial response or final response if no function needed)
            }
        """
        from datetime import datetime

        # Build messages array
        messages = [{"role": "system", "content": FINANCIAL_ADVISOR_SYSTEM_PROMPT}]

        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history[-5:])  # Last 5 messages

        # Add context to user message
        context_info = ""
        if context:
            budget_status = context.get("budget_status", {})
            if budget_status and float(budget_status.get("total_budget", 0)) > 0:
                context_info = f"\n[Current budget: ${float(budget_status.get('total_budget', 0)):.2f}, Spent: ${float(budget_status.get('total_spent', 0)):.2f}]"

        messages.append({
            "role": "user",
            "content": f"{user_message}{context_info}"
        })

        try:
            # Call OpenAI with function calling
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=OPENAI_FUNCTIONS,
                function_call="auto",  # Let AI decide when to call functions
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            message = response.choices[0].message

            # Check if AI wants to call a function
            if message.function_call:
                function_name = message.function_call.name
                function_args = json.loads(message.function_call.arguments)

                # Add user_id to function args
                function_args["user_id"] = user_id

                # Add current month if not specified
                if "month" in OPENAI_FUNCTIONS[0]["parameters"]["properties"] and "month" not in function_args:
                    function_args["month"] = datetime.now().strftime("%Y-%m")

                logger.info(f"AI wants to call function: {function_name} with args: {function_args}")

                return {
                    "requires_function": True,
                    "function_name": function_name,
                    "function_args": function_args,
                    "message": message.content or f"Let me {function_name.replace('_', ' ')} for you..."
                }
            else:
                # No function needed, return direct response
                return {
                    "requires_function": False,
                    "function_name": None,
                    "function_args": None,
                    "message": message.content
                }

        except Exception as e:
            logger.error(f"Chat with functions error: {e}")
            return {
                "requires_function": False,
                "function_name": None,
                "function_args": None,
                "message": "I apologize, but I'm having trouble processing your request right now. Please try again."
            }

    async def generate_function_response(
        self,
        user_message: str,
        function_name: str,
        function_result: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate a natural language response after executing a function

        Args:
            user_message: Original user message
            function_name: Name of function that was called
            function_result: Result from the function execution
            conversation_history: Previous messages

        Returns:
            Natural language response explaining what was done
        """
        # Build context for the AI
        messages = [{"role": "system", "content": FINANCIAL_ADVISOR_SYSTEM_PROMPT}]

        if conversation_history:
            messages.extend(conversation_history[-3:])

        messages.append({"role": "user", "content": user_message})
        messages.append({
            "role": "function",
            "name": function_name,
            "content": json.dumps(function_result)
        })

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating function response: {e}")
            # Fallback response
            if function_name == "create_budget":
                return f"I've created your budget successfully! Total budget: ${function_result.get('total_income', 0):.2f}"
            elif function_name == "log_expense":
                return f"Got it! I've logged ${function_result.get('amount', 0):.2f} for {function_result.get('description', 'your expense')}."
            elif function_name == "analyze_purchase":
                return json.dumps(function_result, indent=2)
            else:
                return "Action completed successfully."

    async def classify_category(
        self,
        merchant: str,
        description: str,
        amount: float,
        categories: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Classify expense into a category using AI

        Args:
            merchant: Merchant name
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
            merchant=merchant,
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
        total_budget = float(budget_summary.get("total_budget", 0))
        total_spent = float(budget_summary.get("total_spent", 0))
        total_remaining = float(budget_summary.get("total_remaining", 0))
        percent_spent = (total_spent / total_budget * 100) if total_budget > 0 else 0

        return f"""
Budget Overview:
- You've spent ${total_spent:.2f} out of ${total_budget:.2f} ({percent_spent:.1f}%)
- Remaining: ${total_remaining:.2f}

{'⚠️ You are overspending in some categories. Review your budget and adjust spending.' if total_spent > total_budget else '✅ You are on track with your budget.'}
"""


# Global AI service instance
ai_service = AIService()
