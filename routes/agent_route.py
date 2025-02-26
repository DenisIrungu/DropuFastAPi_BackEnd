from fastapi import APIRouter, Depends, HTTPException
from utils.auth_middleware import get_current_user

router = APIRouter()

@router.get("/agent/dashboard")
def agent_dashboard(user=Depends(get_current_user)):
    if user["role"] != "agent":
        raise HTTPException(status_code=403, detail="Access denied")
    return {"message": "Welcome to Agent Dashboard"}
