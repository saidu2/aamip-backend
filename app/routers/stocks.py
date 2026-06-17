from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models.stock import Stock, StockPrice, StockFinancial, AIResearch
from app.schemas.stock import StockOut, StockCreate, StockPriceOut, StockFinancialOut, AIResearchOut
from app.utils.security import get_current_user
from app.utils.helpers import log_action

router = APIRouter(prefix="/stocks", tags=["Stocks"])

@router.get("", response_model=list[StockOut])
def list_stocks(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Stock).order_by(Stock.ticker).all()

@router.post("", response_model=StockOut, status_code=201)
def create_stock(payload: StockCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    existing = db.query(Stock).filter(Stock.ticker == payload.ticker.upper()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ticker already exists")
    stock = Stock(**payload.model_dump(), ticker=payload.ticker.upper())
    db.add(stock)
    db.commit()
    db.refresh(stock)
    return stock

@router.get("/{ticker}/prices", response_model=list[StockPriceOut])
def get_prices(ticker: str, limit: int = 60, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(StockPrice).filter(StockPrice.ticker == ticker.upper()).order_by(desc(StockPrice.date)).limit(limit).all()

@router.get("/{ticker}/financials", response_model=list[StockFinancialOut])
def get_financials(ticker: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(StockFinancial).filter(StockFinancial.ticker == ticker.upper()).order_by(desc(StockFinancial.year)).all()

@router.get("/{ticker}/research", response_model=list[AIResearchOut])
def get_research(ticker: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(AIResearch).filter(AIResearch.ticker == ticker.upper()).order_by(desc(AIResearch.created_at)).all()
