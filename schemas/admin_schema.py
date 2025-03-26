from pydantic import BaseModel, EmailStr
from datetime import datetime

class AdminCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class AdminProfileResponse(BaseModel):
    name: str
    profile_picture: str | None

    class Config:
        from_attributes = True

class AdminProfileUpdateResponse(BaseModel):
    profile_picture: str

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
    timestamp: datetime

    class Config:
        from_attributes = True