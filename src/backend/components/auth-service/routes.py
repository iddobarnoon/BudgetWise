from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from typing import Optional
from main import auth_service

router = APIRouter(prefix="/auth", tags=["authentication"])

# Request Models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    monthly_income: Optional[float] = 0.0

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# Dependency for protected routes
async def get_current_user(authorization: str = Header(...)):
    """Extract and validate JWT from Authorization header"""
    try:
        # Extract token from "Bearer <token>"
        token = authorization.replace("Bearer ", "")
        result = await auth_service.validate_token(token)

        if not result.get("valid"):
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        return result

    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

# Endpoints
@router.post("/register")
async def register(request: RegisterRequest):
    """
    Register a new user
    Creates auth user and profile in database
    """
    result = await auth_service.register_user(
        email=request.email,
        password=request.password,
        full_name=request.full_name,
        monthly_income=request.monthly_income
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Registration failed"))

    return {
        "message": "User registered successfully",
        "user_id": result["user_id"],
        "email": result["email"],
        "access_token": result.get("access_token"),
        "refresh_token": result.get("refresh_token")
    }

@router.post("/login")
async def login(request: LoginRequest):
    """
    Authenticate user and return JWT tokens
    """
    result = await auth_service.login(
        email=request.email,
        password=request.password
    )

    if not result.get("success"):
        raise HTTPException(status_code=401, detail=result.get("error", "Invalid credentials"))

    return {
        "message": "Login successful",
        "user_id": result["user_id"],
        "email": result["email"],
        "access_token": result["access_token"],
        "refresh_token": result["refresh_token"],
        "expires_at": result.get("expires_at")
    }

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout user and invalidate session
    """
    # Note: Supabase handles token invalidation on client side
    # Server-side logout is primarily for cleanup
    return {"message": "Logged out successfully"}

@router.post("/refresh")
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    """
    result = await auth_service.refresh_session(request.refresh_token)

    if not result.get("success"):
        raise HTTPException(status_code=401, detail=result.get("error", "Failed to refresh token"))

    return {
        "access_token": result["access_token"],
        "refresh_token": result["refresh_token"],
        "expires_at": result.get("expires_at")
    }

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user's profile
    Requires valid JWT in Authorization header
    """
    return {
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "profile": current_user.get("profile")
    }

@router.get("/validate")
async def validate_token_endpoint(authorization: str = Header(...)):
    """
    Validate a JWT token
    Returns user info if valid, error if not
    """
    try:
        token = authorization.replace("Bearer ", "")
        result = await auth_service.validate_token(token)

        if result.get("valid"):
            return {
                "valid": True,
                "user_id": result["user_id"],
                "email": result["email"]
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid token")

    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
