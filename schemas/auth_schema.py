from pydantic import BaseModel, EmailStr

class AuthLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegistration(BaseModel): 
    email: EmailStr
    password: str
    name: str
    role: str

class UserResponse(BaseModel):
    id: int
    email: str
    role: str

    class Config:
        from_attributes = True