from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from utils.auth_middleware import get_current_user
from services.admin_service import (
    get_admin_profile,
    update_admin_profile_picture,
    create_issue,
    get_urgent_issues,
    get_non_urgent_issues,
    get_admin_preferences,
    update_admin_preferences,
    get_top_regions,
    create_feedback
)
from services.auth_service import register_rider_by_admin, register_agent_by_admin  # Add imports
from schemas.admin_schema import (
    AdminProfileResponse,
    AdminProfileUpdateResponse,
    IssueCreate,
    IssueResponse,
    AdminPreferences,
    AdminPreferencesResponse,
    TopRegionResponse,
    FeedbackCreate,
    FeedbackResponse
)
from schemas.auth_schema import UserRegistration, UserResponse  # Add import

router = APIRouter()

@router.get("/dashboard")
def admin_dashboard(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return {"message": f"Welcome to Admin Dashboard, {current_user['user_id']}"}

@router.get("/profile", response_model=AdminProfileResponse)
def get_profile(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    admin = get_admin_profile(db, current_user["user_id"])
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    return admin

@router.put("/profile", response_model=AdminProfileUpdateResponse)
def update_profile(file: UploadFile = File(...), current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Only JPEG or PNG files are allowed")
    
    profile_picture_url = update_admin_profile_picture(db, current_user["user_id"], file)
    if not profile_picture_url:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    return {"profile_picture": profile_picture_url}

# @router.post("/test-create-issue")
# def test_create_issue(
#     issue_data: IssueCreate,
#     current_user: dict = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     if current_user["role"] != "admin":
#         raise HTTPException(status_code=403, detail="Not authorized")
    
#     issue = create_issue(
#         db,
#         issue_data.description,
#         issue_data.delay_minutes,
#         issue_data.has_direct_customer_impact,
#         issue_data.is_critical_system_failure,
#         issue_data.is_high_priority_complaint,
#         issue_data.is_rider_unavailable
#     )
#     return "Urgent issue" if issue.urgency else "Non-urgent issue"

@router.get("/priorities", response_model=list[IssueResponse])
def get_priorities(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    urgent_issues = get_urgent_issues(db)
    return urgent_issues

@router.get("/notifications", response_model=list[IssueResponse])
def get_notifications(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    non_urgent_issues = get_non_urgent_issues(db)
    return non_urgent_issues

@router.get("/preferences", response_model=AdminPreferencesResponse)
def get_preferences(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "admin":
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
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    updated_preferences = update_admin_preferences(db, current_user["user_id"], preferences.dict())
    if updated_preferences is None:
        raise HTTPException(status_code=404, detail="Admin not found")
    return updated_preferences

@router.get("/top-regions", response_model=list[TopRegionResponse])
def get_top_regions_endpoint(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    top_regions = get_top_regions(db)
    return top_regions

@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(
    feedback: FeedbackCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    feedback_entry = create_feedback(db, current_user["user_id"], "admin", feedback.message)
    return feedback_entry

# Endpoints for registering riders and agents
@router.post("/register-rider", response_model=UserResponse)
def register_rider(
    request: UserRegistration,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    if request.role != "rider":
        raise HTTPException(status_code=400, detail="This endpoint can only register riders")
    user = register_rider_by_admin(db, request)
    if not user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user

@router.post("/register-agent", response_model=UserResponse)
def register_agent(
    request: UserRegistration,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    if request.role != "agent":
        raise HTTPException(status_code=400, detail="This endpoint can only register agents")
    user = register_agent_by_admin(db, request)
    if not user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user