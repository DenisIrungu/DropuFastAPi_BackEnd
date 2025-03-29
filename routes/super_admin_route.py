from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from utils.auth_middleware import get_current_user
from schemas.auth_schema import UserRegistration, UserResponse
from models import Admin
from utils.security import hash_password

router = APIRouter(prefix="/super-admin", tags=["Super Admin"])

@router.post("/register-admin", response_model=UserResponse)
def register_admin(
    request: UserRegistration,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Only super admins can create admins")
    
    if request.role != "admin":
        raise HTTPException(status_code=400, detail="This endpoint can only create admins")
    
    # Check if email already exists
    if db.query(Admin).filter(Admin.email == request.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = hash_password(request.password)
    new_admin = Admin(
        name=request.name,
        email=request.email,
        password=hashed_password,
        role="admin"
    )
    
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return UserResponse(id=new_admin.id, email=new_admin.email, role="admin")