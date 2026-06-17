from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class FXRate(Base):
    __tablename__ = "fx_rates"

    id         = Column(Integer, primary_key=True, index=True)
    date       = Column(Date, nullable=False, index=True)
    usd_ngn    = Column(Float)
    gbp_ngn    = Column(Float)
    eur_ngn    = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MacroIndicator(Base):
    __tablename__ = "macro_indicators"

    id         = Column(Integer, primary_key=True, index=True)
    date       = Column(Date, nullable=False, index=True)
    indicator  = Column(String(200), nullable=False)
    value      = Column(Float, nullable=False)
    source     = Column(String(100))
    notes      = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, index=True)
    user_name  = Column(String(200))
    user_role  = Column(String(50))
    action     = Column(String(300), nullable=False)
    target     = Column(String(200))
    ip_address = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
