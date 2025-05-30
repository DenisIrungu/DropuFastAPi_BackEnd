from sqlalchemy.orm import Session
from models import Admin, Issue, Feedback, VerificationCode, Rider, ResetToken
from schemas.admin_schema import AdminCreate
from utils.security import hash_password
import os
from fastapi import UploadFile
import time
from datetime import datetime
from typing import Optional, List
from sqlalchemy import or_

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
    print(f"Processing file upload for admin_id={user_id}, filename={file.filename}, content_type={file.content_type}")
    
    static_dir = "static/images"
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
        print(f"Created directory: {static_dir}")
    
    timestamp = int(time.time())
    filename = f"admin-{user_id}-{timestamp}{os.path.splitext(file.filename)[1]}"
    file_path = os.path.join(static_dir, filename)
    
    try:
        with open(file_path, "wb") as f:
            content = file.file.read()
            f.write(content)
            print(f"File saved: {file_path}, size={len(content)} bytes")
    except Exception as e:
        print(f"Error saving file: {e}")
        raise
    
    profile_picture_url = f"/static/images/{filename}"
    print(f"Generated profile_picture_url: {profile_picture_url}")
    
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
    return db.query(Issue).filter(Issue.urgency == True).all()

def get_non_urgent_issues(db: Session):
    return db.query(Issue).filter(Issue.urgency == False).all()

def get_admin_preferences(db: Session, user_id: int):
    admin = db.query(Admin).filter(Admin.id == user_id).first()
    if not admin:
        return None
    return admin.preferences or {"theme": "light", "notifications": True}

def update_admin_preferences(db: Session, user_id: int, preferences: dict):
    admin = db.query(Admin).filter(Admin.id == user_id).first()
    if not admin:
        return None
    admin.preferences = preferences
    db.commit()
    db.refresh(admin)
    return admin.preferences

def get_top_regions(db: Session):
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
    feedback = Feedback(
        user_id=user_id,
        user_type=user_type,
        message=message,
        region="Unknown",
        category="General",
        status="Pending",
        rating=0
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback

def get_feedbacks(db: Session, region: Optional[str] = None, date_start: Optional[datetime] = None, 
                 date_end: Optional[datetime] = None, sort_by: str = "date", 
                 sort_order: str = "desc"):
    query = db.query(Feedback)
    if region:
        query = query.filter(Feedback.region.ilike(f"{region}%"))
    if date_start and date_end:
        query = query.filter(Feedback.timestamp.between(date_start, date_end))
    elif date_start:
        query = query.filter(Feedback.timestamp >= date_start)
    elif date_end:
        query = query.filter(Feedback.timestamp <= date_end)
    valid_sort_by = {"date", "rating"}
    if sort_by not in valid_sort_by:
        sort_by = "date"
    valid_sort_order = {"asc", "desc"}
    if sort_order not in valid_sort_order:
        sort_order = "desc"
    if sort_by == "date":
        query = query.order_by(getattr(Feedback.timestamp, sort_order)())
    elif sort_by == "rating":
        query = query.order_by(getattr(Feedback.rating, sort_order)())
    feedbacks = query.all()
    print(f"get_feedbacks: Fetched {len(feedbacks)} feedbacks with region filter: {region}")
    return feedbacks

def delete_admin_account(db: Session, user_id: int):
    print(f"Deleting account for admin_id={user_id}")
    with db.begin():
        admin = db.query(Admin).filter(Admin.id == user_id).first()
        if not admin:
            print(f"Admin not found for admin_id={user_id}")
            return None
        verification_codes_deleted = db.query(VerificationCode).filter(VerificationCode.admin_id == user_id).delete()
        print(f"Deleted {verification_codes_deleted} verification code records for admin_id={user_id}")
        feedback_deleted = db.query(Feedback).filter(Feedback.user_id == user_id, Feedback.user_type == "admin").delete()
        print(f"Deleted {feedback_deleted} feedback records for admin_id={user_id}")
        if admin.profile_picture:
            file_path = admin.profile_picture.lstrip("/")
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Deleted profile picture: {file_path}")
                else:
                    print(f"Profile picture file not found: {file_path}")
            except Exception as e:
                print(f"Error deleting profile picture {file_path}: {e}")
        db.delete(admin)
        print(f"Deleted admin record: id={admin.id}, name={admin.name}, email={admin.email}")
        print(f"Committed deletion for admin_id={user_id}")
    return user_id

def get_riders(db: Session, search: Optional[str] = None, skip: int = 0, limit: int = 10) -> dict:
    """
    Fetch paginated riders with optional filtering by first_name or last_name.
    Returns a dictionary with 'riders' list and 'total' count.
    """
    print(f"Fetching riders with search: {search}, skip: {skip}, limit: {limit}")
    query = db.query(Rider)
    
    # Apply search filter if provided
    if search:
        search = search.strip()
        query = query.filter(
            or_(
                Rider.name.ilike(f"{search}% %"),  # Matches first_name
                Rider.name.ilike(f"% {search}%")   # Matches last_name
            )
        )
    
    # Get total count (including search filter)
    total = query.count()
    print(f"Total riders found: {total}")
    
    # Apply pagination
    riders = query.offset(skip).limit(limit).all()
    print(f"Returned {len(riders)} riders")
    
    return {"riders": riders, "total": total}

def get_rider_by_id(db: Session, rider_id: int) -> Optional[Rider]:
    """
    Fetch a single rider by ID.
    """
    print(f"Fetching rider with ID: {rider_id}")
    rider = db.query(Rider).filter(Rider.id == rider_id).first()
    if rider:
        print(f"Rider found: {rider.name}")
    else:
        print(f"Rider with ID {rider_id} not found")
    return rider

def update_rider_file(rider_id: int, file: UploadFile, file_type: str) -> str:
    """
    Helper function to save rider files (driving_license, insurance).
    """
    print(f"Processing file upload for rider_id={rider_id}, file_type={file_type}, filename={file.filename}, content_type={file.content_type}")
    
    static_dir = "static/uploads/riders"
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
        print(f"Created directory: {static_dir}")
    
    timestamp = int(time.time())
    filename = f"rider-{rider_id}-{file_type}-{timestamp}.pdf"
    file_path = os.path.join(static_dir, filename)
    
    try:
        with open(file_path, "wb") as f:
            content = file.file.read()
            f.write(content)
            print(f"File saved: {file_path}, size={len(content)} bytes")
    except Exception as e:
        print(f"Error saving file: {e}")
        raise
    
    file_url = f"/static/uploads/riders/{filename}"
    print(f"Generated file_url: {file_url}")
    return file_url

def update_rider(db: Session, rider_id: int, update_data: dict, driving_license: Optional[UploadFile] = None, insurance: Optional[UploadFile] = None) -> Optional[Rider]:
    """
    Update an existing rider's details and optionally replace driving license and insurance files.
    """
    print(f"Updating rider with ID: {rider_id}")
    rider = db.query(Rider).filter(Rider.id == rider_id).first()
    if not rider:
        print(f"Rider with ID {rider_id} not found")
        return None

    first_name = update_data.pop("first_name", None)
    last_name = update_data.pop("last_name", None)
    if first_name and last_name:
        rider.name = f"{first_name} {last_name}".strip()
        print(f"Updated name to: {rider.name}")
    elif first_name or last_name:
        existing_name = rider.name.split(" ", 1)
        first_part = existing_name[0] if existing_name else ""
        last_part = existing_name[1] if len(existing_name) > 1 else ""
        rider.name = f"{first_name or first_part} {last_name or last_part}".strip()
        print(f"Updated name to: {rider.name}")

    allowed_fields = {"email", "phone_number", "bike_number", "bike_model", "bike_color", "license", 
                     "emergency_contact_name", "emergency_contact_phone", "emergency_contact_relationship"}
    for key, value in update_data.items():
        if key in allowed_fields and value is not None:
            setattr(rider, key, value)
            print(f"Updated {key} to {value}")

    if driving_license and driving_license.filename:
        print(f"Received driving_license: {driving_license.filename}, content_type: {driving_license.content_type}")
        if driving_license.content_type != "application/pdf":
            raise ValueError(f"Invalid content type for driving_license: {driving_license.content_type}. Only PDFs are allowed")
        if rider.driving_license:
            old_file_path = rider.driving_license.lstrip("/")
            try:
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
                    print(f"Deleted old driving_license: {old_file_path}")
            except Exception as e:
                print(f"Error deleting old driving_license {old_file_path}: {e}")
        driving_license_path = update_rider_file(rider_id, driving_license, "driving_license")
        rider.driving_license = driving_license_path
        print(f"Updated driving_license to: {driving_license_path}")

    if insurance and insurance.filename:
        print(f"Received insurance: {insurance.filename}, content_type: {insurance.content_type}")
        if insurance.content_type != "application/pdf":
            raise ValueError(f"Invalid content type for insurance: {insurance.content_type}. Only PDFs are allowed")
        if rider.insurance:
            old_file_path = rider.insurance.lstrip("/")
            try:
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
                    print(f"Deleted old insurance: {old_file_path}")
            except Exception as e:
                print(f"Error deleting old insurance {old_file_path}: {e}")
        insurance_path = update_rider_file(rider_id, insurance, "insurance")
        rider.insurance = insurance_path
        print(f"Updated insurance to: {insurance_path}")

    db.commit()
    db.refresh(rider)
    print(f"Rider updated: {rider.name}")
    return rider

def delete_rider(db: Session, rider_id: int) -> bool:
    """
    Delete a rider by ID and associated files.
    """
    print(f"Deleting rider with ID: {rider_id}")
    rider = db.query(Rider).filter(Rider.id == rider_id).first()
    if not rider:
        print(f"Rider with ID {rider_id} not found")
        return False

    for file_field in [rider.id_document, rider.driving_license, rider.insurance]:
        if file_field:
            file_path = file_field.lstrip("/")
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

    reset_tokens_deleted = db.query(ResetToken).filter(ResetToken.rider_id == rider_id).delete()
    print(f"Deleted {reset_tokens_deleted} reset tokens for rider_id={rider_id}")

    db.delete(rider)
    db.commit()
    print(f"Rider with ID {rider_id} deleted successfully")
    return True