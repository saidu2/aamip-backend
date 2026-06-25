from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models.stock import Stock, StockPrice, StockFinancial, AIResearch
from app.schemas.stock import StockOut, StockCreate, StockPriceOut, StockFinancialOut, AIResearchOut
from app.utils.security import get_current_user

router = APIRouter(prefix="/stocks", tags=["Stocks"])

def calc_fundamentals(db: Session, ticker: str) -> dict:
    """
    Calculate live fundamentals for a stock from latest price + latest financials.
    Returns dict with pe_ratio, eps_used, price_used, year_used — all None if data missing.
    """
    latest_price = db.query(StockPrice).filter(StockPrice.ticker == ticker).order_by(desc(StockPrice.date)).first()
    latest_fin   = db.query(StockFinancial).filter(StockFinancial.ticker == ticker).order_by(desc(StockFinancial.year)).first()

    result = {
        "pe_ratio":    None,
        "eps":         None,
        "price":       None,
        "price_date":  None,
        "fin_year":    None,
        "revenue":     None,
        "net_profit":  None,
        "roe":         None,   # Return on Equity = net_profit / total_equity
        "debt_to_equity": None,
    }

    if latest_price:
        result["price"]      = latest_price.close_price
        result["price_date"] = str(latest_price.date)

    if latest_fin:
        result["eps"]        = latest_fin.eps
        result["fin_year"]   = latest_fin.year
        result["revenue"]    = latest_fin.revenue
        result["net_profit"] = latest_fin.net_profit

        if latest_fin.total_equity and latest_fin.total_equity != 0 and latest_fin.net_profit:
            result["roe"] = round((latest_fin.net_profit / latest_fin.total_equity) * 100, 2)

        if latest_fin.total_equity and latest_fin.total_equity != 0 and latest_fin.total_debt:
            result["debt_to_equity"] = round(latest_fin.total_debt / latest_fin.total_equity, 2)

    # P/E ratio = Price / EPS (only if both exist and EPS is not zero)
    if result["price"] and result["eps"] and result["eps"] != 0:
        result["pe_ratio"] = round(result["price"] / result["eps"], 2)

    return result

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

@router.get("/fundamentals/all")
def get_all_fundamentals(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Bulk fundamentals for all stocks — used by Stock Research table to show live P/E column."""
    stocks = db.query(Stock).all()
    results = []
    for s in stocks:
        fundamentals = calc_fundamentals(db, s.ticker)
        results.append({
            "ticker": s.ticker,
            "name":   s.name,
            "sector": s.sector,
            "recommendation": s.recommendation,
            "risk_level":     s.risk_level,
            **fundamentals,
        })
    return results

@router.get("/{ticker}/fundamentals")
def get_fundamentals(ticker: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    Returns auto-calculated fundamentals: P/E ratio, ROE, Debt/Equity etc.
    Calculated live from the latest price and latest financials in the database.
    No manual entry needed — updates automatically as new prices/financials are uploaded.
    """
    ticker = ticker.upper()
    stock = db.query(Stock).filter(Stock.ticker == ticker).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    fundamentals = calc_fundamentals(db, ticker)
    return {
        "ticker": ticker,
        "name":   stock.name,
        "sector": stock.sector,
        **fundamentals,
    }

@router.get("/{ticker}/prices", response_model=list[StockPriceOut])
def get_prices(ticker: str, limit: int = 60, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(StockPrice).filter(StockPrice.ticker == ticker.upper()).order_by(desc(StockPrice.date)).limit(limit).all()

@router.get("/{ticker}/financials", response_model=list[StockFinancialOut])
def get_financials(ticker: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(StockFinancial).filter(StockFinancial.ticker == ticker.upper()).order_by(desc(StockFinancial.year)).all()

@router.get("/{ticker}/research", response_model=list[AIResearchOut])
def get_research(ticker: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(AIResearch).filter(AIResearch.ticker == ticker.upper()).order_by(desc(AIResearch.created_at)).all()
