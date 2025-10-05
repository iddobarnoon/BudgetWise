from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router

app = FastAPI(
    title="BudgetWise Auth Service",
    description="User authentication and session management with Supabase",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)

@app.get("/")
async def root():
    return {
        "service": "BudgetWise Auth Service",
        "status": "running",
        "version": "1.0.0",
        "endpoints": [
            "/auth/register",
            "/auth/login",
            "/auth/logout",
            "/auth/refresh",
            "/auth/me",
            "/auth/validate"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🔐 Auth Service Starting...")
    print("="*60)
    print("📍 URL: http://localhost:8001")
    print("📖 Docs: http://localhost:8001/docs")
    print("🔑 Supabase Auth: Enabled")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8001)
