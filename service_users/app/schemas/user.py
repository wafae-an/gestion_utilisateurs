from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    firstname: str
    lastname: str
    phone: Optional[str] = None
    email: EmailStr
    password: str

class UserRegisterResponse(BaseModel):
    id: int
    firstname: str
    lastname: str
    email: str
    role: str
    token: str
    
    class Config:
        from_attributes = True