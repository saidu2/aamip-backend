from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from app.models.stock import Recommendation, RiskLevel

class StockCreate(BaseModel):
    ticker: str
    name: str
    sector: Optional[str] = None
    recommendation: Optional[Recommendation] = Recommendation.HOLD
    risk_level: Optional[RiskLevel] = RiskLevel.MEDIUM

class StockOut(BaseModel):
    id: int
    ticker: str
    name: str
    sector: Optional[str]
    recommendation: str
    risk_level: str

    class Config:
        from_attributes = True

class StockPriceOut(BaseModel):
    id: int
    ticker: str
    date: date
    close_price: float
    open_price: Optional[float]
    high_price: Optional[float]
    low_price: Optional[float]
    volume: Optional[float]

    class Config:
        from_attributes = True

class StockFinancialOut(BaseModel):
    id: int
    ticker: str
    year: int
    revenue: Optional[float]
    net_profit: Optional[float]
    eps: Optional[float]
    pe_ratio: Optional[float]

    class Config:
        from_attributes = True

class AIResearchOut(BaseModel):
    id: int
    ticker: str
    analysis_text: str
    recommendation: Optional[str]
    risk_level: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
