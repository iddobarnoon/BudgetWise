"""
Standalone Budget Engine App - For testing without database
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from decimal import Decimal

app = FastAPI(
    title="BudgetWise Budget Engine",
    description="Budget creation and management service with smart allocation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class CreateBudgetRequest(BaseModel):
    user_id: str
    month: str
    income: Decimal
    goals: List[str] = []

class CheckPurchaseRequest(BaseModel):
    user_id: str
    amount: Decimal
    category_id: str
    month: str

@app.get("/")
async def root():
    return {
        "service": "BudgetWise Budget Engine",
        "status": "running",
        "version": "1.0.0",
        "mode": "standalone"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/budget/create")
async def create_budget(request: CreateBudgetRequest):
    """
    Generate monthly budget (demo mode)
    """
    # Demo allocation using 50/30/20 rule
    needs = float(request.income) * 0.50
    wants = float(request.income) * 0.30
    savings = float(request.income) * 0.20

    return {
        "status": "success",
        "user_id": request.user_id,
        "month": request.month,
        "total_income": float(request.income),
        "allocations": {
            "needs": needs,
            "wants": wants,
            "savings": savings
        },
        "strategy": "50/30/20 Rule",
        "goals": request.goals,
        "message": "Budget created successfully (demo mode - database not connected)"
    }

@app.post("/budget/check-purchase")
async def check_purchase(request: CheckPurchaseRequest):
    """
    Check if purchase fits budget (demo mode)
    """
    # Demo: Assume $500 allocated, $200 spent
    allocated = 500.00
    spent = 200.00
    remaining = allocated - spent

    fits = float(request.amount) <= remaining
    percentage = (float(request.amount) / allocated) * 100

    return {
        "fits_budget": fits,
        "remaining_in_category": remaining,
        "percentage_of_category": round(percentage, 2),
        "alternative_options": [] if fits else [
            "Wait until next month",
            f"Reduce purchase by ${float(request.amount) - remaining:.2f}"
        ],
        "warning": None if fits else f"Exceeds budget by ${float(request.amount) - remaining:.2f}",
        "message": "Demo mode - using sample data"
    }

@app.get("/docs")
async def custom_docs():
    return {
        "message": "Visit /docs for Swagger UI or /redoc for ReDoc"
    }

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 Budget Engine Starting...")
    print("="*60)
    print("📍 URL: http://localhost:8003")
    print("📖 Docs: http://localhost:8003/docs")
    print("✅ Mode: Standalone (no database required)")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8003)
