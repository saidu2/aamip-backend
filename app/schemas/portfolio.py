from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from app.models.portfolio import Currency

class PortfolioCreate(BaseModel):
    name: str
    description: Optional[str] = None
    currency: Currency = Currency.NGN
    inception: Optional[date] = None

class PortfolioOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    currency: str
    inception: Optional[date]
    is_active: int

    class Config:
        from_attributes = True

class HoldingCreate(BaseModel):
    portfolio_id: int
    ticker: str
    quantity: float
    cost_price: float
    purchase_date: Optional[date] = None
    currency: Currency = Currency.NGN
    notes: Optional[str] = None

class HoldingOut(BaseModel):
    id: int
    portfolio_id: int
    ticker: str
    quantity: float
    cost_price: float
    purchase_date: Optional[date]
    currency: str

    class Config:
        from_attributes = True

class HoldingUpdate(BaseModel):
    quantity: Optional[float] = None
    cost_price: Optional[float] = None
    notes: Optional[str] = None
