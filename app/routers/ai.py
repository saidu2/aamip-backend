from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from typing import Optional
import re
from app.database import get_db
from app.models.stock import AIResearch, StockPrice, StockFinancial, Stock, Recommendation, RiskLevel
from app.utils.security import get_current_user
from app.utils.helpers import log_action
from app.services.ai_service import analyze_stock, analyze_portfolio
from app.config import settings

router = APIRouter(prefix="/ai", tags=["AI"])

class StockAnalysisRequest(BaseModel):
    ticker: str

class PortfolioAnalysisRequest(BaseModel):
    portfolio_id: int
    metrics: dict

def extract_recommendation(text: str) -> Optional[str]:
    """Extract BUY/HOLD/SELL from AI analysis text."""
    patterns = [
        r'RECOMMENDATION[:\s]+\*?\*?(BUY|HOLD|SELL)\*?\*?',
        r'\b(BUY|HOLD|SELL)\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text.upper())
        if match:
            return match.group(1)
    return None

def extract_risk_level(text: str) -> Optional[str]:
    """Extract LOW/MEDIUM/HIGH risk from AI analysis text."""
    patterns = [
        r'RISK\s+SCORE[:\s]+\*?\*?(LOW|MEDIUM|HIGH)\*?\*?',
        r'RISK\s+LEVEL[:\s]+\*?\*?(LOW|MEDIUM|HIGH)\*?\*?',
    ]
    for pattern in patterns:
        match = re.search(pattern, text.upper())
        if match:
            return match.group(1)
    return None

@router.post("/analyze-stock")
async def run_stock_analysis(
    payload: StockAnalysisRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if not settings.GEMINI_API_KEY:
        raise HTTPException(status_code=503, detail="AI service not configured. Add GEMINI_API_KEY to .env")

    ticker = payload.ticker.upper()
    stock  = db.query(Stock).filter(Stock.ticker == ticker).first()

    # Get latest financials and prices
    financials   = db.query(StockFinancial).filter(StockFinancial.ticker == ticker).order_by(desc(StockFinancial.year)).first()
    latest_price = db.query(StockPrice).filter(StockPrice.ticker == ticker).order_by(desc(StockPrice.date)).first()

    financials_dict = {
        "revenue":    financials.revenue    if financials else "N/A",
        "net_profit": financials.net_profit if financials else "N/A",
        "eps":        financials.eps        if financials else "N/A",
        "year":       financials.year       if financials else "N/A",
    }
    prices_dict = {
        "latest_price": latest_price.close_price if latest_price else "N/A",
        "date":         str(latest_price.date)   if latest_price else "N/A",
    }

    try:
        analysis_text = await analyze_stock(
            ticker     = ticker,
            name       = stock.name   if stock else ticker,
            sector     = stock.sector if stock else "N/A",
            financials = financials_dict,
            prices     = prices_dict,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

    # ── Auto-update stock signals from AI result ──────────────────────────────
    recommendation = extract_recommendation(analysis_text)
    risk_level     = extract_risk_level(analysis_text)

    if stock:
        updated_fields = []
        if recommendation and recommendation in [r.value for r in Recommendation]:
            stock.recommendation = Recommendation(recommendation)
            updated_fields.append(f"recommendation={recommendation}")
        if risk_level and risk_level in [r.value for r in RiskLevel]:
            stock.risk_level = RiskLevel(risk_level)
            updated_fields.append(f"risk_level={risk_level}")
        if updated_fields:
            db.commit()

    # Save to research repository
    research = AIResearch(
        ticker        = ticker,
        analyst_id    = current_user.id,
        analysis_text = analysis_text,
        recommendation= Recommendation(recommendation) if recommendation and recommendation in [r.value for r in Recommendation] else None,
        risk_level    = RiskLevel(risk_level)          if risk_level     and risk_level     in [r.value for r in RiskLevel]     else None,
        model_used    = "gemini-2.0-flash",
    )
    db.add(research)
    db.commit()
    db.refresh(research)
    log_action(db, current_user, "Generated AI stock analysis", target=ticker)

    return {
        "ticker":         ticker,
        "analysis":       analysis_text,
        "research_id":    research.id,
        "recommendation": recommendation,
        "risk_level":     risk_level,
        "signals_updated": bool(recommendation or risk_level),
    }

@router.post("/analyze-portfolio")
async def run_portfolio_analysis(
    payload: PortfolioAnalysisRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if not settings.GEMINI_API_KEY:
        raise HTTPException(status_code=503, detail="AI service not configured")

    from app.models.portfolio import Portfolio, Holding
    portfolio = db.query(Portfolio).filter(Portfolio.id == payload.portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    holdings = db.query(Holding).filter(Holding.portfolio_id == payload.portfolio_id).all()
    holdings_list = [{"ticker": h.ticker, "quantity": h.quantity, "cost_price": h.cost_price} for h in holdings]

    try:
        analysis_text = await analyze_portfolio(
            name     = portfolio.name,
            holdings = holdings_list,
            metrics  = payload.metrics,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

    log_action(db, current_user, "Generated AI portfolio analysis", target=portfolio.name)
    return {"portfolio": portfolio.name, "analysis": analysis_text}
