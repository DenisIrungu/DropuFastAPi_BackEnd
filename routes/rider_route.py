from fastapi import APIRouter, Depends, HTTPException
from utils.auth_middleware import get_current_user

router = APIRouter()

@router.get("/rider/dashboard")
def rider_dashboard(user=Depends(get_current_user)):
    if user["role"] != "rider":
        raise HTTPException(status_code=403, detail="Access denied")
    return {"message": "Welcome to Rider Dashboard"}
