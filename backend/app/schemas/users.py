from uuid import UUID
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    name: str
    surname: str
    email: EmailStr
    username: str
    role: str
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int = 1
    per_page: int = 100
    has_next: bool = False
    has_prev: bool = False

# Login Schema
class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: UUID
    email: str

# User Profile Schema
class UserProfile(BaseModel):
    id: UUID
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Admin User Management Schemas
class UserListItem(BaseModel):
    """Schema per lista utenti in admin"""
    id: UUID
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    crm_id: Optional[int] = None
    class Config:
        from_attributes = True

class UserDetailResponse(BaseModel):
    """Schema per dettagli completi utente"""
    id: UUID
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    role: str
    is_active: bool
    permissions: Optional[dict] = None
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    must_change_password: Optional[bool] = False
    
    class Config:
        from_attributes = True
