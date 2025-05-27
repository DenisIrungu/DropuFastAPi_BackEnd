from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from database import get_db
from utils.auth_middleware import get_current_user
from utils.email_service import send_verification_code
import random
from services.admin_service import (
    get_admin_profile,
    update_admin_profile_picture,
    create_issue,
    get_urgent_issues,
    get_non_urgent_issues,
    get_admin_preferences,
    update_admin_preferences,
    get_top_regions,
    create_feedback,
    get_feedbacks,
    delete_admin_account
)
from services.auth_service import register_rider_by_admin, register_agent_by_admin, resend_rider_verification_email
from schemas.admin_schema import (
    AdminProfileResponse,
    AdminProfileUpdateResponse,
    IssueCreate,
    IssueResponse,
    AdminPreferences,
    AdminPreferencesResponse,
    TopRegionResponse,
    FeedbackCreate,
    FeedbackResponse,
    AdminProfileUpdate,
    DeleteAccountResponse
)
from schemas.auth_schema import UserRegistration, UserResponse, RiderRegistration
from models import Admin, VerificationCode, Rider
from utils.security import hash_password
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter()

@router.get("/dashboard")
def admin_dashboard(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    return {"message": f"Welcome to Admin Dashboard, {current_user['user_id']}"}

@router.get("/profile", response_model=AdminProfileResponse)
def get_profile(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    admin = get_admin_profile(db, current_user["user_id"])
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    print(f"GET /admin/profile response: {admin.__dict__}")
    return admin

@router.put("/profile", response_model=AdminProfileUpdateResponse)
def update_profile(
    file: UploadFile = File(None),
    name: str = Form(None),
    email: str = Form(None),
    password: str = Form(None),
    verification_code: str = Form(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    admin = db.query(Admin).filter(Admin.id == current_user["user_id"]).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    update_data = AdminProfileUpdate(
        name=name,
        email=email,
        password=password,
        verification_code=verification_code
    )
    
    print(f"Incoming file: {file.filename if file else 'No file'}")
    print(f"File content type: {file.content_type if file else 'None'}")
    
    # Handle profile picture update only if a file is provided
    profile_picture_url = admin.profile_picture
    if file and file.filename:  # Ensure a file is actually provided
        if file.content_type not in ["image/jpeg", "image/png"]:
            error_msg = f"Invalid content type: {file.content_type}. Only JPEG or PNG files are allowed"
            print(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
        profile_picture_url = update_admin_profile_picture(db, current_user["user_id"], file)
        if not profile_picture_url:
            raise HTTPException(status_code=404, detail="Admin not found")
        admin.profile_picture = profile_picture_url
        print(f"Updated profile_picture: {profile_picture_url}")
    # If no file is provided, do NOT reset profile_picture (it retains its existing value)
    
    if update_data.name:
        admin.name = update_data.name
    
    print(f"Incoming update_data: email={update_data.email}, password={update_data.password}, verification_code={update_data.verification_code}")
    
    if update_data.email or update_data.password:
        if not update_data.verification_code:
            error_msg = "Verification code required for email or password updates"
            print(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
        
        if not (update_data.verification_code.isdigit() and len(update_data.verification_code) == 6):
            error_msg = "Verification code must be a 6-digit number"
            print(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
        
        verification = db.query(VerificationCode).filter(
            VerificationCode.admin_id == current_user["user_id"],
            VerificationCode.code == update_data.verification_code,
            VerificationCode.expires_at > datetime.utcnow()
        ).first()
        
        if not verification:
            error_msg = "Invalid or expired verification code"
            print(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
        
        print(f"Verification type: {verification.type}, Email update requested: {bool(update_data.email)}, Password update requested: {bool(update_data.password)}")
        
        if update_data.email:
            if verification.type != "email":
                error_msg = "Verification code type mismatch: expected 'email'"
                print(error_msg)
                raise HTTPException(status_code=400, detail=error_msg)
            admin.email = update_data.email
            print(f"Updated email to: {admin.email}")
        if update_data.password:
            if verification.type != "password":
                error_msg = "Verification code type mismatch: expected 'password'"
                print(error_msg)
                raise HTTPException(status_code=400, detail=error_msg)
            admin.password = hash_password(update_data.password)
            print(f"Updated password")
    elif update_data.verification_code:
        error_msg = "Verification code provided but no email or password update requested"
        print(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    
    db.flush()
    db.commit()
    db.refresh(admin)
    print(f"After commit - Admin: name={admin.name}, email={admin.email}, profile_picture={admin.profile_picture}")
    
    if update_data.email or update_data.password:
        db.query(VerificationCode).filter(
            VerificationCode.admin_id == current_user["user_id"],
            VerificationCode.code == update_data.verification_code
        ).delete()
        db.commit()
    
    response = {"name": admin.name, "email": admin.email, "profile_picture": admin.profile_picture}
    print(f"PUT /admin/profile response: {response}")
    return response

@router.get("/priorities", response_model=list[IssueResponse])
def get_priorities(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    urgent_issues = get_urgent_issues(db)
    return urgent_issues

@router.get("/notifications", response_model=list[IssueResponse])
def get_notifications(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    non_urgent_issues = get_non_urgent_issues(db)
    return non_urgent_issues

@router.get("/preferences", response_model=AdminPreferencesResponse)
def get_preferences(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    preferences = get_admin_preferences(db, current_user["user_id"])
    if preferences is None:
        raise HTTPException(status_code=404, detail="Admin not found")
    return preferences

@router.put("/preferences", response_model=AdminPreferencesResponse)
def update_preferences(
    preferences: AdminPreferences,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    updated_preferences = update_admin_preferences(db, current_user["user_id"], preferences.dict())
    if updated_preferences is None:
        raise HTTPException(status_code=404, detail="Admin not found")
    return updated_preferences

@router.get("/top-regions", response_model=list[TopRegionResponse])
def get_top_regions_endpoint(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    top_regions = get_top_regions(db)
    return top_regions

@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(
    feedback: FeedbackCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    feedback_entry = create_feedback(db, current_user["user_id"], "admin", feedback.message)
    return feedback_entry

@router.get("/feedbacks", response_model=list[FeedbackResponse])
def get_feedbacks_endpoint(
    region: Optional[str] = None,
    date_start: Optional[str] = None,
    date_end: Optional[str] = None,
    sort_by: str = "date",
    sort_order: str = "desc",
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Parse date strings to datetime objects if provided
    start_date = datetime.fromisoformat(date_start) if date_start else None
    end_date = datetime.fromisoformat(date_end) if date_end else None
    
    # Fetch feedbacks with filters and sorting
    feedbacks = get_feedbacks(db, region, start_date, end_date, sort_by, sort_order)
    
    return feedbacks

@router.post("/register-rider", response_model=UserResponse)
def register_rider(
    first_name: str = Form(...),
    last_name: str = Form(...),
    phone_number: str = Form(...),
    email: str = Form(...),
    bike_model: str = Form(...),
    bike_color: str = Form(...),
    plate_number: str = Form(...),
    license: str = Form(...),
    id_document: UploadFile = File(...),
    driving_license: UploadFile = File(...),
    insurance: UploadFile = File(...),
    emergency_contact_name: str = Form(...),
    emergency_contact_phone: str = Form(...),
    emergency_contact_relationship: str = Form(...),
    terms_accepted: bool = Form(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Validate terms acceptance
    if not terms_accepted:
        raise HTTPException(status_code=400, detail="Terms and conditions must be accepted")

    # Validate PDF files with detailed logging
    files = [id_document, driving_license, insurance]
    for file in files:
        print(f"Received file: {file.filename}, content_type: {file.content_type}, size: {file.size} bytes")
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail=f"File {file.filename} must be a PDF")

    # Prepare rider registration data
    rider_data = RiderRegistration(
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        email=email,
        bike_model=bike_model,
        bike_color=bike_color,
        plate_number=plate_number,
        license=license,
        id_document=id_document,
        driving_license=driving_license,
        insurance=insurance,
        emergency_contact_name=emergency_contact_name,
        emergency_contact_phone=emergency_contact_phone,
        emergency_contact_relationship=emergency_contact_relationship,
        role="rider"
    )

    # Call service to register rider
    user = register_rider_by_admin(db, rider_data, current_user["user_id"])
    if not user:
        raise HTTPException(status_code=400, detail="Email already registered")

    return user

@router.post("/register-agent", response_model=UserResponse)
def register_agent(
    request: UserRegistration,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    if request.role != "agent":
        raise HTTPException(status_code=400, detail="This endpoint can only register agents")
    user = register_agent_by_admin(db, request)
    if not user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user

@router.post("/send-verification-code")
def send_verification_code_endpoint(
    type: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if type not in ["email", "password"]:
        raise HTTPException(status_code=400, detail="Invalid type. Must be 'email' or 'password'")
    
    admin = db.query(Admin).filter(Admin.id == current_user["user_id"]).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    db.query(VerificationCode).filter(
        VerificationCode.admin_id == current_user["user_id"],
        VerificationCode.type == type
    ).delete()
    db.commit()
    
    code = str(random.randint(100000, 999999))
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    verification = VerificationCode(
        admin_id=admin.id,
        code=code,
        type=type,
        expires_at=expires_at
    )
    db.add(verification)
    db.commit()
    
    if not send_verification_code(admin.email, code):
        raise HTTPException(status_code=500, detail="Failed to send verification code")
    
    return {"message": "Verification code sent to your email"}

@router.post("/verify-code")
def verify_code(
    code: str,
    type: str,
    new_value: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if type not in ["email", "password"]:
        raise HTTPException(status_code=400, detail="Invalid type. Must be 'email' or 'password'")
    
    admin = db.query(Admin).filter(Admin.id == current_user["user_id"]).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    verification = db.query(VerificationCode).filter(
        VerificationCode.admin_id == current_user["user_id"],
        VerificationCode.code == code,
        VerificationCode.type == type,
        VerificationCode.expires_at > datetime.utcnow()
    ).first()
    
    if not verification:
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")
    
    if type == "email":
        admin.email = new_value
    elif type == "password":
        admin.password = hash_password(new_value)
    
    db.delete(verification)
    db.commit()
    db.refresh(admin)
    
    return {"message": f"{type.capitalize()} updated successfully"}

@router.post("/resend-verification-email", response_model=UserResponse)
def resend_verification_email(
    email: str = Form(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Call the service to resend the email
    return resend_rider_verification_email(db, email, current_user["user_id"])

@router.post("/delete-account", response_model=DeleteAccountResponse)
def delete_account(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete the admin's account permanently."""
    if current_user["role"] not in ["admin", "super_admin"]:
        print(f"Unauthorized attempt to delete account by user_id={current_user['user_id']}, role={current_user['role']}")
        raise HTTPException(status_code=403, detail="Not authorized")
    
    print(f"Processing account deletion for user_id={current_user['user_id']}")
    result = delete_admin_account(db, current_user["user_id"])
    if result is None:
        print(f"Account deletion failed: admin_id={current_user['user_id']} not found")
        raise HTTPException(status_code=404, detail="Admin not found")
    
    print(f"Account deletion successful for user_id={current_user['user_id']}")
    return {"message": "Account deleted successfully"}