from pydantic import BaseModel, EmailStr

class AdminCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
