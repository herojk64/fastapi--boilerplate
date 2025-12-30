from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr


# Base schema with shared fields
class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = True


# Schema for creating a new user
class UserCreate(UserBase):
    password: str


# Schema for updating user
class UserUpdate(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None  # optional for updates


# Schema for returning user data
class UserOut(UserBase):
    id: int
    fullname: Optional[str] = None  # optional computed property
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
