from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models.market import FXRate, MacroIndicator, AuditLog
from app.models.stock import StockPrice
from app.utils.security import get_current_user

router = APIRouter(prefix="/market", tags=["Market"])

@router.get("/fx-rates")
def get_fx_rates(limit: int = 30, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(FXRate).order_by(desc(FXRate.date)).limit(limit).all()

@router.get("/fx-rates/latest")
def get_latest_fx(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    rate = db.query(FXRate).order_by(desc(FXRate.date)).first()
    return rate

@router.get("/macro")
def get_macro(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Return latest value for each indicator
    subq = db.query(
        MacroIndicator.indicator,
        db.query(MacroIndicator.id).filter(
            MacroIndicator.indicator == MacroIndicator.indicator
        ).order_by(desc(MacroIndicator.date)).limit(1).correlate(MacroIndicator).scalar_subquery()
    )
    indicators = db.query(MacroIndicator).order_by(MacroIndicator.indicator, desc(MacroIndicator.date)).all()
    seen = set()
    result = []
    for i in indicators:
        if i.indicator not in seen:
            seen.add(i.indicator)
            result.append(i)
    return result

@router.get("/prices/movers")
def get_movers(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Get top gainers and losers based on latest two price entries per ticker"""
    latest = db.query(StockPrice).order_by(desc(StockPrice.date)).limit(200).all()
    tickers = {}
    for p in latest:
        if p.ticker not in tickers:
            tickers[p.ticker] = []
        if len(tickers[p.ticker]) < 2:
            tickers[p.ticker].append(p)

    movers = []
    for ticker, prices in tickers.items():
        if len(prices) >= 2:
            today_price = prices[0].close_price
            prev_price  = prices[1].close_price
            change      = ((today_price - prev_price) / prev_price) * 100 if prev_price else 0
            movers.append({"ticker": ticker, "price": today_price, "change": round(change, 2)})

    movers.sort(key=lambda x: x["change"], reverse=True)
    return {
        "gainers": movers[:5],
        "losers":  list(reversed(movers[-5:])),
    }

@router.get("/audit-log")
def get_audit_log(limit: int = 100, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(AuditLog).order_by(desc(AuditLog.created_at)).limit(limit).all()
