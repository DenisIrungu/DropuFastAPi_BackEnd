import email
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

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
    region: str  
    category: str  
    status: str  
    rating: int  
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

# Refined schemas for rider management
class RiderResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone_number: str
    bike_number: str
    bike_model: str
    bike_color: str
    license: str
    id_document: str
    driving_license: str
    insurance: str
    emergency_contact_name: str
    emergency_contact_phone: str
    emergency_contact_relationship: str
    created_by: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class RiderUpdate(BaseModel):
    first_name: Optional[str] = None  # Will combine with last_name to form name
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    bike_number: Optional[str] = None
    bike_model: Optional[str] = None
    bike_color: Optional[str] = None
    license: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None

class RiderUpdateResponse(RiderResponse):
    pass

class PaginatedRiderResponse(BaseModel):
    total: int
    skip: int
    limit: int
    riders: List[RiderResponse]

    class Config:
        from_attributes = True