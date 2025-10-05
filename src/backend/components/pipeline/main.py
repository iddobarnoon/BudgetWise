# -*- coding: utf-8 -*-
"""
Entry point for BudgetWise AI Pipeline Service
Run this file to start the AI service
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    import uvicorn
    from app import app

    print("\n" + "="*70)
    print("BudgetWise AI Pipeline Service")
    print("="*70)
    print("Starting service on http://localhost:8004")
    print("API Documentation: http://localhost:8004/docs")
    print("Powered by OpenAI GPT-4o-mini")
    print("="*70)
    print("\nPress CTRL+C to stop the service\n")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8004,
        log_level="info",
        reload=True
    )
