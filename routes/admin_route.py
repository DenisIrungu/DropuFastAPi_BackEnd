from fastapi import APIRouter, Depends, HTTPException
from utils.auth_middleware import get_current_user

router = APIRouter()

@router.get("/admin/dashboard")
def admin_dashboard(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return {"message": "Welcome to Admin Dashboard"}
