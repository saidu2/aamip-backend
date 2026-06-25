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
from app.routers.stocks import calc_fundamentals

router = APIRouter(prefix="/ai", tags=["AI"])

class StockAnalysisRequest(BaseModel):
    ticker: str

class PortfolioAnalysisRequest(BaseModel):
    portfolio_id: int
    metrics: dict

def extract_recommendation(text: str) -> Optional[str]:
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

    # ── Auto-calculated fundamentals: P/E, ROE, Debt/Equity ───────────────────
    fundamentals = calc_fundamentals(db, ticker)

    financials_dict = {
        "revenue":         fundamentals.get("revenue")    or "N/A",
        "net_profit":      fundamentals.get("net_profit") or "N/A",
        "eps":             fundamentals.get("eps")         or "N/A",
        "year":            fundamentals.get("fin_year")    or "N/A",
        "pe_ratio":        fundamentals.get("pe_ratio")    or "N/A (insufficient data)",
        "roe_percent":     fundamentals.get("roe")         or "N/A",
        "debt_to_equity":  fundamentals.get("debt_to_equity") or "N/A",
    }
    prices_dict = {
        "latest_price": fundamentals.get("price")      or "N/A",
        "date":         fundamentals.get("price_date")  or "N/A",
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
        if recommendation and recommendation in [r.value for r in Recommendation]:
            stock.recommendation = Recommendation(recommendation)
        if risk_level and risk_level in [r.value for r in RiskLevel]:
            stock.risk_level = RiskLevel(risk_level)
        db.commit()

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
        "ticker":          ticker,
        "analysis":        analysis_text,
        "research_id":     research.id,
        "recommendation":  recommendation,
        "risk_level":      risk_level,
        "signals_updated": bool(recommendation or risk_level),
        "fundamentals_used": fundamentals,
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
