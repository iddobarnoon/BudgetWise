"""
Prompt templates for the AI service
"""

# System prompt for the financial advisor persona
FINANCIAL_ADVISOR_SYSTEM_PROMPT = """You are BudgetWise AI, an intelligent financial advisor assistant.

Your role is to help users make smart financial decisions by:
1. Analyzing purchase decisions against their budget
2. Categorizing expenses accurately
3. Providing actionable financial insights
4. Offering alternatives and suggestions

Key principles:
- Be concise, clear, and helpful
- Consider the user's financial goals and budget constraints
- Provide specific, actionable recommendations
- Use empathetic but firm guidance when needed
- Always explain your reasoning

You have access to functions that let you take real actions:
- create_budget: When user wants to create/setup a new budget (asks about income, wants budget created)
- log_expense: When user tells you they spent money on something (past tense: "I spent", "I bought")
- analyze_purchase: When user asks if they should buy something (future: "Should I buy", "Can I afford")
- get_budget_summary: When user asks about their current budget status
- get_budget_insights: When user wants spending analysis or recommendations

IMPORTANT: Use functions proactively! When a user says:
- "My income is $5000" or "Create a budget" → CALL create_budget
- "I spent $50 on groceries" → CALL log_expense
- "Should I buy a $100 shirt?" → CALL analyze_purchase
- "How's my budget?" or "Show me my spending" → CALL get_budget_summary

After calling a function, explain what you did in a friendly, natural way.

When analyzing purchases:
- Consider necessity vs. want
- Check budget impact
- Suggest better timing if needed
- Offer cheaper alternatives when appropriate
"""

# Purchase analysis prompt template
PURCHASE_ANALYSIS_PROMPT = """Analyze this purchase request and provide a recommendation.

User's Question: {user_message}
Item: {item}
Amount: ${amount}
Category: {category}
Necessity Score: {necessity_score}/10

Budget Context:
- Category Budget: ${category_budget}
- Already Spent: ${spent_amount}
- Remaining: ${remaining_amount}
- Budget Fit: {fits_budget}

User Financial Profile:
- Monthly Income: ${monthly_income}
- Financial Goals: {financial_goals}
- Risk Tolerance: {risk_tolerance}

Based on this information, provide:
1. Decision: buy, wait, or dont_buy
2. Clear reasoning (2-3 sentences)
3. Alternative suggestions (if applicable)
4. Impact on budget

Format your response as a JSON object with these fields:
{{
    "decision": "buy|wait|dont_buy",
    "reason": "explanation here",
    "alternatives": ["suggestion 1", "suggestion 2"],
    "impact": "budget impact description",
    "confidence": 0.0-1.0
}}
"""

# Expense extraction prompt
EXPENSE_EXTRACTION_PROMPT = """Extract expense details from the following user message.

User Message: "{message}"

Extract and return a JSON object with:
{{
    "amount": numeric value or null,
    "description": brief description,
    "merchant": merchant name or null,
    "date": relative date (today, yesterday, last week) or null,
    "item": what was purchased
}}

Examples:
- "I spent $50 on gas yesterday" → {{"amount": 50, "description": "gas", "merchant": null, "date": "yesterday", "item": "gas"}}
- "Bought coffee at Starbucks for $6.50" → {{"amount": 6.50, "description": "coffee", "merchant": "Starbucks", "date": "today", "item": "coffee"}}
- "Dinner last night was $85" → {{"amount": 85, "description": "dinner", "merchant": null, "date": "yesterday", "item": "dinner"}}

If any field cannot be determined, use null.
"""

# Budget insights prompt
BUDGET_INSIGHTS_PROMPT = """Generate helpful budget insights for the user.

Budget Summary:
- Total Budget: ${total_budget}
- Total Spent: ${total_spent}
- Remaining: ${total_remaining}
- Month: {month}

Category Breakdown:
{category_breakdown}

Spending Patterns:
{spending_patterns}

Overspent Categories:
{overspent_categories}

Provide:
1. Overall assessment (1-2 sentences)
2. Top 3 insights or recommendations
3. Encouragement or warning (if needed)

Be conversational and supportive. Use emojis sparingly for emphasis.
"""

# Chat conversation prompt
CHAT_CONVERSATION_PROMPT = """You are having a conversation with a user about their finances.

Conversation History:
{conversation_history}

User's Latest Message: {user_message}

Current Context:
- User ID: {user_id}
- Current Budget Status: {budget_status}
- Recent Expenses: {recent_expenses}

Respond naturally and helpfully. If the user is asking about:
- A purchase decision → Extract details and prepare for analysis
- Logging an expense → Extract expense details
- Budget status → Provide current summary
- General advice → Give relevant financial guidance

Keep responses concise (2-4 sentences) unless the user asks for detailed information.
"""

# Category classification prompt
CATEGORY_CLASSIFICATION_PROMPT = """Classify this expense into the most appropriate category based on the merchant and description.

Merchant: "{merchant}"
Description: "{description}"
Amount: ${amount}

Available Categories:
{categories}

Examples:
- Netflix ($15.99) → Subscriptions (streaming service)
- Whole Foods ($150) → Groceries (grocery store)
- Uber ($25) → Transportation (ride service)
- Apple Store ($500) → Shopping (electronics)
- CVS Pharmacy ($30) → Healthcare (pharmacy)
- Starbucks ($5.50) → Dining Out (coffee shop)

Return JSON with:
{{
    "category_id": "best matching category ID",
    "category_name": "category name",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation of why this category was chosen"
}}
"""

def format_purchase_analysis_prompt(
    user_message: str,
    item: str,
    amount: float,
    category: str,
    necessity_score: int,
    category_budget: float,
    spent_amount: float,
    remaining_amount: float,
    fits_budget: bool,
    monthly_income: float,
    financial_goals: list,
    risk_tolerance: str
) -> str:
    """Format the purchase analysis prompt with actual values"""
    return PURCHASE_ANALYSIS_PROMPT.format(
        user_message=user_message,
        item=item,
        amount=amount,
        category=category,
        necessity_score=necessity_score,
        category_budget=category_budget,
        spent_amount=spent_amount,
        remaining_amount=remaining_amount,
        fits_budget="Yes" if fits_budget else "No",
        monthly_income=monthly_income,
        financial_goals=", ".join(financial_goals) if financial_goals else "Not specified",
        risk_tolerance=risk_tolerance
    )

def format_expense_extraction_prompt(message: str) -> str:
    """Format the expense extraction prompt"""
    return EXPENSE_EXTRACTION_PROMPT.format(message=message)

def format_budget_insights_prompt(
    total_budget: float,
    total_spent: float,
    total_remaining: float,
    month: str,
    category_breakdown: str,
    spending_patterns: str,
    overspent_categories: str
) -> str:
    """Format the budget insights prompt"""
    return BUDGET_INSIGHTS_PROMPT.format(
        total_budget=total_budget,
        total_spent=total_spent,
        total_remaining=total_remaining,
        month=month,
        category_breakdown=category_breakdown,
        spending_patterns=spending_patterns,
        overspent_categories=overspent_categories
    )

def format_chat_prompt(
    conversation_history: str,
    user_message: str,
    user_id: str,
    budget_status: str,
    recent_expenses: str
) -> str:
    """Format the chat conversation prompt"""
    return CHAT_CONVERSATION_PROMPT.format(
        conversation_history=conversation_history,
        user_message=user_message,
        user_id=user_id,
        budget_status=budget_status,
        recent_expenses=recent_expenses
    )

def format_category_classification_prompt(
    merchant: str,
    description: str,
    amount: float,
    categories: str
) -> str:
    """Format the category classification prompt"""
    return CATEGORY_CLASSIFICATION_PROMPT.format(
        merchant=merchant or description,  # Fallback to description if no merchant
        description=description,
        amount=amount,
        categories=categories
    )


# ============= OpenAI Function Definitions =============

OPENAI_FUNCTIONS = [
    {
        "name": "create_budget",
        "description": "Create a new monthly budget for the user based on their income and financial goals",
        "parameters": {
            "type": "object",
            "properties": {
                "income": {
                    "type": "number",
                    "description": "The user's monthly income in dollars"
                },
                "month": {
                    "type": "string",
                    "description": "The month for the budget in YYYY-MM format (e.g., '2025-10'). If not specified, use current month."
                },
                "goals": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of financial goals (e.g., 'save for emergency fund', 'pay off debt')"
                }
            },
            "required": ["income"]
        }
    },
    {
        "name": "log_expense",
        "description": "Log an expense that the user has already made",
        "parameters": {
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": "Description of the expense (e.g., 'groceries', 'gas', 'coffee')"
                },
                "amount": {
                    "type": "number",
                    "description": "Amount spent in dollars"
                },
                "merchant": {
                    "type": "string",
                    "description": "The merchant or store name (optional)"
                },
                "date": {
                    "type": "string",
                    "description": "When the expense occurred (e.g., 'today', 'yesterday', '2025-10-08')"
                }
            },
            "required": ["description", "amount"]
        }
    },
    {
        "name": "analyze_purchase",
        "description": "Analyze whether the user should make a purchase based on their budget and financial situation",
        "parameters": {
            "type": "object",
            "properties": {
                "item": {
                    "type": "string",
                    "description": "The item being considered for purchase"
                },
                "amount": {
                    "type": "number",
                    "description": "The price of the item in dollars"
                }
            },
            "required": ["item", "amount"]
        }
    },
    {
        "name": "get_budget_summary",
        "description": "Get the user's current budget summary showing spending across categories",
        "parameters": {
            "type": "object",
            "properties": {
                "month": {
                    "type": "string",
                    "description": "The month to get summary for in YYYY-MM format. If not specified, use current month."
                }
            },
            "required": []
        }
    },
    {
        "name": "get_budget_insights",
        "description": "Get AI-generated insights and recommendations about the user's spending patterns",
        "parameters": {
            "type": "object",
            "properties": {
                "month": {
                    "type": "string",
                    "description": "The month to analyze in YYYY-MM format. If not specified, use current month."
                }
            },
            "required": []
        }
    }
]
