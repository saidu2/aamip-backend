from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    admin              = "admin"
    analyst            = "analyst"
    portfolio_manager  = "portfolio_manager"
    compliance         = "compliance"
    executive          = "executive"

class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True)
    full_name  = Column(String, nullable=False)
    email      = Column(String, unique=True, index=True, nullable=False)
    password   = Column(String, nullable=False)
    role       = Column(Enum(UserRole), default=UserRole.analyst)
    firm       = Column(String, default="Prime Capital & Investment Ltd")
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
