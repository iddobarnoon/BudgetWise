from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from routes import router

app = FastAPI(
    title="BudgetWise Budget Engine",
    description="Budget creation and management service with smart allocation",
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
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
