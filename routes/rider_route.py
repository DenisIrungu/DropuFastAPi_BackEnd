from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from database import get_db
from utils.auth_middleware import get_current_user
from models import Rider, ResetToken
from utils.security import hash_password
from datetime import datetime

router = APIRouter(tags=["Rider"])

@router.get("/dashboard")
def rider_dashboard(user=Depends(get_current_user)):
    if user["role"] != "rider":
        raise HTTPException(status_code=403, detail="Access denied")
    return {"message": "Welcome to Rider Dashboard"}

@router.post("/reset-password")
async def reset_password(
    token: str = Form(...),
    new_password: str = Form(...),
    db: Session = Depends(get_db)
):
    reset_token = db.query(ResetToken).filter(ResetToken.token == token).first()
    if not reset_token:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    if reset_token.expires_at < datetime.utcnow():
        db.delete(reset_token)
        db.commit()
        raise HTTPException(status_code=400, detail="Token has expired")

    rider = db.query(Rider).filter(Rider.id == reset_token.rider_id).first()
    if not rider:
        db.delete(reset_token)
        db.commit()
        raise HTTPException(status_code=404, detail="Rider not found")

    rider.password = hash_password(new_password)
    db.delete(reset_token)
    db.commit()

    return {"message": "Password reset successfully"}