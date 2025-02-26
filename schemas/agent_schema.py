from pydantic import BaseModel, EmailStr

class AgentCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    station_location: str
