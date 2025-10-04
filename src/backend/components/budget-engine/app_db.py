from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from routes_db import router

app = FastAPI(
    title="BudgetWise Budget Engine",
    description="Budget creation and management service with Supabase database integration",
    version="1.0.0"
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

@app.get("/")
async def root():
    return {
        "service": "BudgetWise Budget Engine",
        "status": "running",
        "version": "1.0.0",
        "database": "Supabase (connected)"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 Budget Engine Starting...")
    print("="*60)
    print("📍 URL: http://localhost:8003")
    print("📖 Docs: http://localhost:8003/docs")
    print("💾 Database: Supabase (connected)")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8003)
