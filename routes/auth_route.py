from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from database import get_db
from services.auth_service import authenticate_user, register_user
from schemas.auth_schema import AuthLogin, UserRegistration, UserResponse
from utils.auth_middleware import get_current_user

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(request: UserRegistration, db: Session = Depends(get_db)):
    user = register_user(db, request)
    if not user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user

@router.post("/login")
def login(request: AuthLogin, response: Response, db: Session = Depends(get_db)):
    user_data = authenticate_user(db, request)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    role = user_data["role"]
    user_id = user_data["user_id"]
    
    response.set_cookie(
        key="session",
        value=f"{user_id}|{role}",
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax"
    )
    return {"message": "Login successful"}

@router.post("/logout")
def logout(response: Response, current_user: dict = Depends(get_current_user)):
    response.set_cookie(
        key="session",
        value="",
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        expires=0
    )
    return {"message": "Logout successful"}