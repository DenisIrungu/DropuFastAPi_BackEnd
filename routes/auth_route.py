from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from database import get_db
from schemas.auth_schema import AuthLogin, UserRegistration
from services.auth_service import authenticate_user, create_user
from utils.security import create_session, destroy_session

router = APIRouter()

@router.post("/register")
def register(request: UserRegistration, db: Session = Depends(get_db)):
    user = create_user(db, request)
    if not user:
        raise HTTPException(status_code=400, detail="User registration failed")
    return {"message": "User registered successfully"}

@router.post("/login")
def login(request: AuthLogin, response: Response, db: Session = Depends(get_db)):
    user_data = authenticate_user(db, request)

    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user = user_data["user"]
    role = user_data["role"]

    create_session(response, user.id, role)  
    return {
        "message": "Login successful",
        "redirect": f"/{role}/dashboard",
        "role": role  
    }
@router.post("/logout")
def logout(response: Response):
    destroy_session(response)
    return {"message": "Logout successful"}
