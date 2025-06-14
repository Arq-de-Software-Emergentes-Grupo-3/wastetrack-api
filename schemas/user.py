from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Literal["worker", "citizen"]
    address: str
    phone: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    guid: str
    name: str
    email: EmailStr
    role: str
    address: str
    phone: str
    latitude: Optional[str]
    longitude: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    name: Optional[str]
    phone: Optional[str]
    role: Optional[Literal["worker", "citizen"]]

