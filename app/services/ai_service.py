import httpx
from app.config import settings

GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_URL   = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

async def call_gemini(prompt: str) -> str:
    if not settings.GEMINI_API_KEY:
        raise ValueError("Gemini API key not configured")

    async with httpx.AsyncClient(timeout=30.0) as client:
        res = await client.post(
            f"{GEMINI_URL}?key={settings.GEMINI_API_KEY}",
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.3, "maxOutputTokens": 1200},
            },
        )
        res.raise_for_status()
        data = res.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

async def analyze_stock(ticker: str, name: str, sector: str, financials: dict, prices: dict) -> str:
    prompt = f"""
You are a senior investment analyst at a Nigerian SEC-regulated asset management firm.
Analyze the following NGX-listed stock and provide a concise institutional research note.

Stock: {name} ({ticker})
Sector: {sector}
Financial Data: {financials}
Market Data: {prices}

Provide your analysis in this format:

COMPANY OVERVIEW
[2-3 sentences about what the company does and its market position in Nigeria]

FINANCIAL HEALTH
[Assessment of profitability, revenue trend, and balance sheet]

VALUATION
[Is the stock cheap or expensive relative to NGX sector peers?]

KEY RISKS
• [Risk 1]
• [Risk 2]
• [Risk 3]

RECOMMENDATION: BUY / HOLD / SELL
[One clear sentence explaining why]

RISK SCORE: LOW / MEDIUM / HIGH
[One sentence on the main risk driver]

Keep the tone professional and institutional.
"""
    return await call_gemini(prompt)

async def analyze_portfolio(name: str, holdings: list, metrics: dict) -> str:
    holdings_text = "\n".join([f"- {h['ticker']} ({h.get('sector','N/A')}): {h.get('weight',0):.1f}% weight" for h in holdings])
    prompt = f"""
You are a senior portfolio manager at a Nigerian SEC-regulated asset management firm.
Provide an institutional portfolio assessment.

Portfolio: {name}
YTD Return: {metrics.get('ytd', 'N/A')}%
Sharpe Ratio: {metrics.get('sharpe', 'N/A')}
Volatility: {metrics.get('volatility', 'N/A')}%
Max Drawdown: {metrics.get('max_drawdown', 'N/A')}%

Holdings:
{holdings_text}

Provide your assessment in this format:

PORTFOLIO OVERVIEW
[2-3 sentences on strategy and overall performance]

DIVERSIFICATION ASSESSMENT
[Sector concentration and diversification analysis for a Nigerian fund]

PERFORMANCE COMMENTARY
[Commentary on YTD return, Sharpe ratio, and volatility]

KEY RISKS
• [Risk 1]
• [Risk 2]
• [Risk 3]

REBALANCING SUGGESTIONS
[Specific actionable suggestions based on actual holdings]
"""
    return await call_gemini(prompt)
