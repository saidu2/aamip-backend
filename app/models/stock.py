from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum

class Recommendation(str, enum.Enum):
    BUY  = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"

class RiskLevel(str, enum.Enum):
    LOW    = "LOW"
    MEDIUM = "MEDIUM"
    HIGH   = "HIGH"

class Stock(Base):
    __tablename__ = "stocks"

    id             = Column(Integer, primary_key=True, index=True)
    ticker         = Column(String(20), unique=True, index=True, nullable=False)
    name           = Column(String(200), nullable=False)
    sector         = Column(String(100))
    industry       = Column(String(100))
    description    = Column(Text)
    recommendation = Column(Enum(Recommendation), default=Recommendation.HOLD)
    risk_level     = Column(Enum(RiskLevel), default=RiskLevel.MEDIUM)
    created_at     = Column(DateTime(timezone=True), server_default=func.now())
    updated_at     = Column(DateTime(timezone=True), onupdate=func.now())


class StockPrice(Base):
    __tablename__ = "stock_prices"

    id            = Column(Integer, primary_key=True, index=True)
    ticker        = Column(String(20), index=True, nullable=False)
    date          = Column(Date, nullable=False)
    open_price    = Column(Float)
    high_price    = Column(Float)
    low_price     = Column(Float)
    close_price   = Column(Float, nullable=False)
    volume        = Column(Float)
    market_cap    = Column(Float)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())


class StockFinancial(Base):
    __tablename__ = "stock_financials"

    id           = Column(Integer, primary_key=True, index=True)
    ticker       = Column(String(20), index=True, nullable=False)
    year         = Column(Integer, nullable=False)
    revenue      = Column(Float)
    net_profit   = Column(Float)
    eps          = Column(Float)
    total_assets = Column(Float)
    total_equity = Column(Float)
    total_debt   = Column(Float)
    dividends    = Column(Float)
    pe_ratio     = Column(Float)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())


class AIResearch(Base):
    __tablename__ = "ai_research"

    id             = Column(Integer, primary_key=True, index=True)
    ticker         = Column(String(20), index=True, nullable=False)
    analyst_id     = Column(Integer, index=True)
    analysis_text  = Column(Text, nullable=False)
    recommendation = Column(Enum(Recommendation))
    risk_level     = Column(Enum(RiskLevel))
    model_used     = Column(String(100))
    created_at     = Column(DateTime(timezone=True), server_default=func.now())
