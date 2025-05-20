from pydantic import BaseModel, EmailStr
from fastapi import UploadFile
from typing import Optional

class AuthLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegistration(BaseModel): 
    email: EmailStr
    password: str
    name: str
    role: str

class RiderRegistration(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    email: EmailStr
    bike_model: str
    bike_color: str
    plate_number: str
    license: str
    id_document: UploadFile
    driving_license: UploadFile
    insurance: UploadFile
    emergency_contact_name: str
    emergency_contact_phone: str
    emergency_contact_relationship: str
    role: str

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    message: Optional[str] = None

    class Config:
        from_attributes = True