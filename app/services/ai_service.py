import httpx
from app.config import settings

GROQ_URL   = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-70b-8192"

async def call_ai(prompt: str) -> str:
    """
    Calls Groq API (free, no card required).
    Falls back to Gemini if GEMINI_API_KEY is set and GROQ_API_KEY is not.
    """
    if settings.GROQ_API_KEY:
        return await call_groq(prompt)
    elif settings.GEMINI_API_KEY:
        return await call_gemini(prompt)
    else:
        raise ValueError("No AI API key configured. Add GROQ_API_KEY or GEMINI_API_KEY to .env")

async def call_groq(prompt: str) -> str:
    if not settings.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not configured")

    async with httpx.AsyncClient(timeout=30.0) as client:
        res = await client.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 1200,
            },
        )
        res.raise_for_status()
        data = res.json()
        return data["choices"][0]["message"]["content"]

async def call_gemini(prompt: str) -> str:
    GEMINI_MODEL = "gemini-2.0-flash"
    GEMINI_URL   = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

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
Analyze the following NGX-listed stock and produce a concise institutional research note.
Base your recommendation strictly on the actual figures provided — do not invent numbers.

Stock: {name} ({ticker})
Sector: {sector}

KEY FUNDAMENTALS:
- Latest Price:           {prices.get('latest_price')} (as of {prices.get('date')})
- EPS (Earnings/Share):   {financials.get('eps')}
- P/E Ratio:              {financials.get('pe_ratio')}
- Revenue:                {financials.get('revenue')} (FY {financials.get('year')})
- Net Profit:             {financials.get('net_profit')}
- ROE (Return on Equity): {financials.get('roe_percent')}%
- Debt-to-Equity Ratio:   {financials.get('debt_to_equity')}

If any figure shows "N/A", note that data is missing and adjust confidence accordingly.

Provide your analysis in this exact format:

COMPANY OVERVIEW
[2-3 sentences about what the company does and its market position in Nigeria]

FINANCIAL HEALTH
[Assessment using ROE and Debt-to-Equity. State the actual numbers.]

VALUATION
[Assessment using P/E ratio vs NGX sector peers. State the actual P/E number.]

KEY RISKS
• [Risk 1]
• [Risk 2]
• [Risk 3]

RECOMMENDATION: BUY / HOLD / SELL
[One clear sentence referencing specific financial metrics]

RISK SCORE: LOW / MEDIUM / HIGH
[One sentence on the main risk driver]
"""
    return await call_ai(prompt)

async def analyze_portfolio(name: str, holdings: list, metrics: dict) -> str:
    holdings_text = "\n".join([
        f"- {h['ticker']}: {h.get('weight', 0):.1f}% weight, P&L: {h.get('pnl_pct', 0):.1f}%"
        for h in holdings
    ])
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
[Sector concentration analysis for a Nigerian fund]

PERFORMANCE COMMENTARY
[Commentary on YTD return and risk-adjusted performance]

KEY RISKS
• [Risk 1 specific to actual holdings]
• [Risk 2]
• [Risk 3]

REBALANCING SUGGESTIONS
[Specific actionable suggestions based on actual holdings and weights]
"""
    return await call_ai(prompt)
