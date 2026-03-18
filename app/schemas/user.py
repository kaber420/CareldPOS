from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from app.models.user import UserRole


class UserBase(BaseModel):
    """Schema base de usuario"""
    username: str
    email: str
    full_name: str
    role: UserRole = UserRole.RECEPTIONIST
    phone: Optional[str] = None


class UserCreate(UserBase):
    """Schema para crear usuario"""
    password: str


class UserUpdate(BaseModel):
    """Schema para actualizar usuario"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema de respuesta de usuario"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    """Respuesta de token"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Datos del token"""
    username: Optional[str] = None
    exp: Optional[int] = None
