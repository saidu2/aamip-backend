from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.portfolio import Portfolio, Holding
from app.models.stock import StockPrice
from sqlalchemy import desc
from app.schemas.portfolio import PortfolioCreate, PortfolioOut, HoldingCreate, HoldingOut, HoldingUpdate
from app.utils.security import get_current_user
from app.utils.helpers import log_action

router = APIRouter(prefix="/portfolios", tags=["Portfolios"])

@router.get("", response_model=list[PortfolioOut])
def list_portfolios(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Portfolio).filter(Portfolio.is_active == 1).all()

@router.post("", response_model=PortfolioOut, status_code=201)
def create_portfolio(payload: PortfolioCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    p = Portfolio(**payload.model_dump(), manager_id=current_user.id)
    db.add(p)
    db.commit()
    db.refresh(p)
    log_action(db, current_user, "Created portfolio", target=p.name)
    return p

@router.get("/{portfolio_id}", response_model=PortfolioOut)
def get_portfolio(portfolio_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    p = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return p

@router.get("/{portfolio_id}/holdings")
def get_holdings(portfolio_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio_id).all()
    result = []
    for h in holdings:
        latest_price = db.query(StockPrice).filter(
            StockPrice.ticker == h.ticker
        ).order_by(desc(StockPrice.date)).first()

        current_price = latest_price.close_price if latest_price else h.cost_price
        current_value = h.quantity * current_price
        cost_value    = h.quantity * h.cost_price
        pnl           = current_value - cost_value
        pnl_pct       = ((pnl / cost_value) * 100) if cost_value else 0

        result.append({
            "id":            h.id,
            "ticker":        h.ticker,
            "quantity":      h.quantity,
            "cost_price":    h.cost_price,
            "current_price": current_price,
            "current_value": current_value,
            "cost_value":    cost_value,
            "pnl":           pnl,
            "pnl_pct":       round(pnl_pct, 2),
            "purchase_date": str(h.purchase_date) if h.purchase_date else None,
            "currency":      h.currency,
        })

    total_value = sum(r["current_value"] for r in result)
    for r in result:
        r["weight"] = round((r["current_value"] / total_value * 100), 2) if total_value else 0

    return result

@router.post("/{portfolio_id}/holdings", response_model=HoldingOut, status_code=201)
def add_holding(portfolio_id: int, payload: HoldingCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    p = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    h = Holding(**payload.model_dump())
    db.add(h)
    db.commit()
    db.refresh(h)
    log_action(db, current_user, "Added holding", target=f"{payload.ticker} → {p.name}")
    return h

@router.put("/{portfolio_id}/holdings/{holding_id}", response_model=HoldingOut)
def update_holding(portfolio_id: int, holding_id: int, payload: HoldingUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    h = db.query(Holding).filter(Holding.id == holding_id, Holding.portfolio_id == portfolio_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Holding not found")
    if payload.quantity is not None:   h.quantity   = payload.quantity
    if payload.cost_price is not None: h.cost_price = payload.cost_price
    if payload.notes is not None:      h.notes      = payload.notes
    db.commit()
    db.refresh(h)
    return h

@router.delete("/{portfolio_id}/holdings/{holding_id}")
def delete_holding(portfolio_id: int, holding_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    h = db.query(Holding).filter(Holding.id == holding_id, Holding.portfolio_id == portfolio_id).first()
    if not h:
        raise HTTPException(status_code=404, detail="Holding not found")
    db.delete(h)
    db.commit()
    log_action(db, current_user, "Deleted holding", target=h.ticker)
    return {"message": "Holding deleted"}
