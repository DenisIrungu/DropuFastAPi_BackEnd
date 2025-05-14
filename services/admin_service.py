from sqlalchemy.orm import Session
from models import Admin, Issue, Feedback, VerificationCode
from schemas import AdminCreate
from utils.security import hash_password
import os
from fastapi import UploadFile
import time
from datetime import datetime
from typing import Optional

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
    """Retrieve all admins with a display_id for gap-free numbering."""
    admins = db.query(Admin).all()
    # Add display_id starting from 1
    return [
        {
            "display_id": index + 1,
            "id": admin.id,
            "name": admin.name,
            "email": admin.email,
            "profile_picture": admin.profile_picture
        }
        for index, admin in enumerate(admins)
    ]

def get_admin_profile(db: Session, user_id: int):
    admin = db.query(Admin).filter(Admin.id == user_id).first()
    if not admin:
        return None
    return admin

def update_admin_profile_picture(db: Session, user_id: int, file: UploadFile):
    # Log the start of the process
    print(f"Processing file upload for admin_id={user_id}, filename={file.filename}, content_type={file.content_type}")
    
    # Define the directory to save profile pictures
    static_dir = "static/images"  # Fix directory name to match URL path
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
        print(f"Created directory: {static_dir}")
    
    # Generate a unique filename
    timestamp = int(time.time())
    filename = f"admin-{user_id}-{timestamp}{os.path.splitext(file.filename)[1]}"
    file_path = os.path.join(static_dir, filename)
    
    # Save the file
    try:
        with open(file_path, "wb") as f:
            content = file.file.read()
            f.write(content)
            print(f"File saved: {file_path}, size={len(content)} bytes")
    except Exception as e:
        print(f"Error saving file: {e}")
        raise
    
    # Construct the profile picture URL (use relative path to avoid hardcoding domain)
    profile_picture_url = f"/static/images/{filename}"
    print(f"Generated profile_picture_url: {profile_picture_url}")
    
    # Update the admin's profile picture in the database
    admin = db.query(Admin).filter(Admin.id == user_id).first()
    if not admin:
        print(f"Admin not found for admin_id={user_id}")
        return None
    admin.profile_picture = profile_picture_url
    db.commit()
    db.refresh(admin)
    print(f"Updated admin profile_picture to: {admin.profile_picture}")
    
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

def get_feedbacks(db: Session, region: Optional[str] = None, date_start: Optional[datetime] = None, 
                 date_end: Optional[datetime] = None, sort_by: str = "date", 
                 sort_order: str = "desc"):
    """Fetch feedback entries with optional filtering and sorting."""
    # Start with the base query
    query = db.query(Feedback)

    # Apply filters
    if region:
        # Use ilike for case-insensitive prefix matching (PostgreSQL)
        query = query.filter(Feedback.region.ilike(f"{region}%"))
        # For MySQL, comment out the above line and use:
        # query = query.filter(Feedback.region.like(f"{region}%"))
    
    if date_start and date_end:
        query = query.filter(Feedback.timestamp.between(date_start, date_end))
    elif date_start:
        query = query.filter(Feedback.timestamp >= date_start)
    elif date_end:
        query = query.filter(Feedback.timestamp <= date_end)

    # Validate sort_by and sort_order
    valid_sort_by = {"date", "rating"}
    if sort_by not in valid_sort_by:
        sort_by = "date"  # Default to date if invalid
    valid_sort_order = {"asc", "desc"}
    if sort_order not in valid_sort_order:
        sort_order = "desc"  # Default to desc if invalid

    # Apply sorting
    if sort_by == "date":
        query = query.order_by(getattr(Feedback.timestamp, sort_order)())
    elif sort_by == "rating":
        query = query.order_by(getattr(Feedback.rating, sort_order)())

    # Execute the query and return results
    feedbacks = query.all()
    print(f"get_feedbacks: Fetched {len(feedbacks)} feedbacks with region filter: {region}")
    return feedbacks

def delete_admin_account(db: Session, user_id: int):
    """Delete an admin account, associated profile picture, verification codes, and feedback."""
    print(f"Deleting account for admin_id={user_id}")
    
    # Start a transaction
    with db.begin():
        # Fetch the admin
        admin = db.query(Admin).filter(Admin.id == user_id).first()
        if not admin:
            print(f"Admin not found for admin_id={user_id}")
            return None
        
        # Delete verification code records
        verification_codes_deleted = db.query(VerificationCode).filter(VerificationCode.admin_id == user_id).delete()
        print(f"Deleted {verification_codes_deleted} verification code records for admin_id={user_id}")
        
        # Delete feedback records
        feedback_deleted = db.query(Feedback).filter(Feedback.user_id == user_id, Feedback.user_type == "admin").delete()
        print(f"Deleted {feedback_deleted} feedback records for admin_id={user_id}")
        
        # Delete profile picture file if it exists
        if admin.profile_picture:
            file_path = admin.profile_picture.lstrip("/")  # Convert /static/images/... to static/images/...
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Deleted profile picture: {file_path}")
                else:
                    print(f"Profile picture file not found: {file_path}")
            except Exception as e:
                print(f"Error deleting profile picture {file_path}: {e}")
                # Continue deletion even if file deletion fails
        
        # Delete the admin record
        db.delete(admin)
        print(f"Deleted admin record: id={admin.id}, name={admin.name}, email={admin.email}")
        
        # Commit is handled by db.begin(), but we'll log it
        print(f"Committed deletion for admin_id={user_id}")
    
    return user_id