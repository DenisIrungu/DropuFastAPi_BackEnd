from sqlalchemy.orm import Session
from models import Admin, Issue, Feedback
from schemas import AdminCreate
from utils.security import hash_password
import os
from fastapi import UploadFile
import time
from datetime import datetime

def create_admin(db: Session, admin_data: AdminCreate):
    """Create a new admin."""
    new_admin = Admin(
        name=admin_data.name,
        email=admin_data.email,
        password=hash_password(admin_data.password),
        preferences={"theme": "light", "notifications": True}
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin

def get_admins(db: Session):
    """Retrieve all admins."""
    return db.query(Admin).all()

def get_admin_profile(db: Session, user_id: int):
    admin = db.query(Admin).filter(Admin.id == user_id).first()
    if not admin:
        return None
    return admin

def update_admin_profile_picture(db: Session, user_id: int, file: UploadFile):
    static_dir = "statics/images"
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    
    timestamp = int(time.time())
    filename = f"admin-{user_id}-{timestamp}{os.path.splitext(file.filename)[1]}"
    file_path = os.path.join(static_dir, filename)
    
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    
    profile_picture_url = f"http://localhost:8000/static/images/{filename}"
    
    admin = db.query(Admin).filter(Admin.id == user_id).first()
    if not admin:
        return None
    admin.profile_picture = profile_picture_url
    db.commit()
    db.refresh(admin)
    return profile_picture_url

def create_issue(
    db: Session,
    description: str,
    delay_minutes: int = 0,
    has_direct_customer_impact: bool = False,
    is_critical_system_failure: bool = False,
    is_high_priority_complaint: bool = False,
    is_rider_unavailable: bool = False
):
    """Create an issue and automatically determine urgency based on all factors."""
    is_urgent = (
        delay_minutes > 30 or
        has_direct_customer_impact or
        is_critical_system_failure or
        is_high_priority_complaint or
        is_rider_unavailable
    )
    
    new_issue = Issue(
        description=description,
        urgency=is_urgent,
        timestamp=datetime.utcnow(),
        status="open"
    )
    db.add(new_issue)
    db.commit()
    db.refresh(new_issue)
    return new_issue

def get_urgent_issues(db: Session):
    """Fetch all urgent issues (urgency=True)."""
    return db.query(Issue).filter(Issue.urgency == True).all()

def get_non_urgent_issues(db: Session):
    """Fetch all non-urgent issues (urgency=False)."""
    return db.query(Issue).filter(Issue.urgency == False).all()

def get_admin_preferences(db: Session, user_id: int):
    """Fetch the admin's preferences."""
    admin = db.query(Admin).filter(Admin.id == user_id).first()
    if not admin:
        return None
    return admin.preferences or {"theme": "light", "notifications": True}

def update_admin_preferences(db: Session, user_id: int, preferences: dict):
    """Update the admin's preferences."""
    admin = db.query(Admin).filter(Admin.id == user_id).first()
    if not admin:
        return None
    admin.preferences = preferences
    db.commit()
    db.refresh(admin)
    return admin.preferences

def get_top_regions(db: Session):
    """Fetch the top 5 regions by performance (simulated data)."""
    all_regions = [
        {"region": "Westlands", "success_rate": 95.5},
        {"region": "Embakasi", "success_rate": 92.0},
        {"region": "Kasarani", "success_rate": 88.7},
        {"region": "Lang'ata", "success_rate": 85.3},
        {"region": "Dagoretti", "success_rate": 80.1},
        {"region": "Starehe", "success_rate": 78.6},
        {"region": "Kamukunji", "success_rate": 76.2},
        {"region": "Makadara", "success_rate": 74.8},
        {"region": "Ruaraka", "success_rate": 73.4},
        {"region": "Mathare", "success_rate": 71.9}
    ]
    sorted_regions = sorted(all_regions, key=lambda x: x["success_rate"], reverse=True)
    return sorted_regions[:5]

def create_feedback(db: Session, user_id: int, user_type: str, message: str):
    """Create a new feedback entry."""
    feedback = Feedback(
        user_id=user_id,
        user_type=user_type,
        message=message
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback