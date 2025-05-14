import email
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class AdminCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class AdminProfileResponse(BaseModel):
    name: str
    email: str
    profile_picture: str | None

    class Config:
        from_attributes = True

class AdminProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    verification_code: Optional[str] = None

class AdminProfileUpdateResponse(BaseModel):
    name: str
    email: str
    profile_picture: Optional[str] = None  

class IssueCreate(BaseModel):
    description: str
    delay_minutes: int = 0
    has_direct_customer_impact: bool = False
    is_critical_system_failure: bool = False
    is_high_priority_complaint: bool = False
    is_rider_unavailable: bool = False

class IssueResponse(BaseModel):
    id: int
    description: str
    urgency: bool
    timestamp: datetime
    status: str

    class Config:
        from_attributes = True

class AdminPreferences(BaseModel):
    theme: str = "light"
    notifications: bool = True

class AdminPreferencesResponse(AdminPreferences):
    pass

class TopRegionResponse(BaseModel):
    region: str
    success_rate: float

class FeedbackCreate(BaseModel):
    message: str

class FeedbackResponse(BaseModel):
    id: int
    user_id: int  
    user_type: str 
    message: str
    region: str  # New field
    category: str  # New field
    status: str  # New field
    rating: int  # New field
    timestamp: datetime

    class Config:
        from_attributes = True

class DeleteAccountResponse(BaseModel):
    message: str

class AdminListResponse(BaseModel):
    display_id: int
    id: int
    name: str
    email: str
    profile_picture: Optional[str] = None

    class Config:
        from_attributes = True