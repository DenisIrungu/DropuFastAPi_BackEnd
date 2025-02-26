from pydantic import BaseModel, EmailStr

class RiderCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    bike_number: str
