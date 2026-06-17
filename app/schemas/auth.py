from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import UserRole

class LoginRequest(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.analyst
    firm: Optional[str] = "Prime Capital & Investment Ltd"

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    firm: str
    is_active: bool

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
