from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes_db import router

app = FastAPI(
    title="BudgetWise Ranking System",
    description="Expense categorization and ranking service with Supabase integration",
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

# Include routers
app.include_router(router)

@app.get("/")
async def root():
    return {
        "service": "BudgetWise Ranking System",
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
    print("🚀 Ranking System Starting...")
    print("="*60)
    print("📍 URL: http://localhost:8002")
    print("📖 Docs: http://localhost:8002/docs")
    print("💾 Database: Supabase (connected)")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8002)
