from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum

class Currency(str, enum.Enum):
    NGN = "NGN"
    USD = "USD"

class Portfolio(Base):
    __tablename__ = "portfolios"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(200), nullable=False)
    description = Column(Text)
    manager_id  = Column(Integer, index=True)
    currency    = Column(Enum(Currency), default=Currency.NGN)
    inception   = Column(Date)
    is_active   = Column(Integer, default=1)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())


class Holding(Base):
    __tablename__ = "holdings"

    id           = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), index=True)
    ticker       = Column(String(20), nullable=False)
    quantity     = Column(Float, nullable=False)
    cost_price   = Column(Float, nullable=False)
    purchase_date= Column(Date)
    currency     = Column(Enum(Currency), default=Currency.NGN)
    notes        = Column(Text)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    updated_at   = Column(DateTime(timezone=True), onupdate=func.now())


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    id           = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), index=True)
    date         = Column(Date, nullable=False)
    total_value  = Column(Float)
    total_cost   = Column(Float)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
