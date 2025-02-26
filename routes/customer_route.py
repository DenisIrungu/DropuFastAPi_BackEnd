from fastapi import APIRouter, Depends, HTTPException
from utils.auth_middleware import get_current_user

router = APIRouter()

@router.get("/customer/dashboard")
def customer_dashboard(user=Depends(get_current_user)):
    if user["role"] != "customer":
        raise HTTPException(status_code=403, detail="Access denied")
    return {"message": "Welcome to Customer Dashboard"}
