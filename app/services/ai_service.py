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
Analyze the following NGX-listed stock using the fundamental data provided and produce
a concise, fact-grounded institutional research note. Base your recommendation on the
actual numbers given — do not invent figures that are not provided.

Stock: {name} ({ticker})
Sector: {sector}

KEY FUNDAMENTALS (auto-calculated from latest uploaded data):
- Latest Price:        {prices.get('latest_price')} (as of {prices.get('date')})
- EPS (Earnings/Share): {financials.get('eps')}
- P/E Ratio:           {financials.get('pe_ratio')}
- Revenue:             {financials.get('revenue')} (FY {financials.get('year')})
- Net Profit:          {financials.get('net_profit')}
- ROE (Return on Equity): {financials.get('roe_percent')}%
- Debt-to-Equity Ratio: {financials.get('debt_to_equity')}

If any figure shows "N/A", explicitly note that this data has not yet been uploaded
and that the recommendation confidence is limited accordingly — do not fabricate a number.

Provide your analysis in this exact format:

COMPANY OVERVIEW
[2-3 sentences about what the company does and its market position in Nigeria]

FINANCIAL HEALTH
[Assess profitability and balance sheet strength using the ROE and Debt-to-Equity figures above. State the actual numbers in your reasoning.]

VALUATION
[Assess whether the stock is cheap or expensive using the P/E ratio given. Compare qualitatively to typical NGX sector multiples. State the actual P/E number in your reasoning.]

KEY RISKS
• [Risk 1 — tie to the data where possible, e.g. high debt-to-equity]
• [Risk 2]
• [Risk 3]

RECOMMENDATION: BUY / HOLD / SELL
[One clear sentence explaining why, explicitly referencing the P/E ratio, EPS, or ROE figures used]

RISK SCORE: LOW / MEDIUM / HIGH
[One sentence on the main risk driver]

Keep the tone professional, factual, and institutional. If fundamental data is missing (N/A), recommend HOLD with a note that more data is needed for a confident call.
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

Provide:

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
