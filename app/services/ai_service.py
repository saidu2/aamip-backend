import httpx
from app.config import settings

CLAUDE_URL   = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-haiku-4-5-20251001"

async def call_ai(prompt: str) -> str:
    if settings.ANTHROPIC_API_KEY:
        return await call_claude(prompt)
    elif settings.GROQ_API_KEY:
        return await call_groq(prompt)
    elif settings.GEMINI_API_KEY:
        return await call_gemini(prompt)
    else:
        raise ValueError("No AI API key configured.")

async def call_claude(prompt: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(
                CLAUDE_URL,
                headers={
                    "x-api-key":         settings.ANTHROPIC_API_KEY.strip(),
                    "anthropic-version": "2023-06-01",
                    "Content-Type":      "application/json",
                },
                json={
                    "model":      CLAUDE_MODEL,
                    "max_tokens": 1200,
                    "messages":   [{"role": "user", "content": prompt}],
                },
            )
            if not res.is_success:
                error_body = res.text
                raise ValueError(f"Anthropic API error {res.status_code}: {error_body}")
            data = res.json()
            return data["content"][0]["text"]
    except httpx.HTTPStatusError as e:
        raise ValueError(f"Anthropic HTTP error: {e.response.text}")
    except Exception as e:
        raise ValueError(f"Claude call failed: {str(e)}")

async def call_groq(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=30.0) as client:
        res = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}", "Content-Type": "application/json"},
            json={"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3, "max_tokens": 1200},
        )
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]

async def call_gemini(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=30.0) as client:
        res = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={settings.GEMINI_API_KEY}",
            json={"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.3, "maxOutputTokens": 1200}},
        )
        res.raise_for_status()
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]

async def analyze_stock(ticker: str, name: str, sector: str, financials: dict, prices: dict) -> str:
    has_data = any(v not in [None, "N/A"] for v in [financials.get("pe_ratio"), financials.get("eps"), financials.get("revenue")])

    if has_data:
        data_section = f"""UPLOADED FINANCIAL DATA:
- Latest Price: {prices.get('latest_price')} (as of {prices.get('date')})
- EPS: {financials.get('eps')}
- P/E Ratio: {financials.get('pe_ratio')}
- Revenue: {financials.get('revenue')} (FY {financials.get('year')})
- Net Profit: {financials.get('net_profit')}
- ROE: {financials.get('roe_percent')}%
- Debt-to-Equity: {financials.get('debt_to_equity')}"""
    else:
        data_section = """No financial data uploaded yet. Use your training knowledge of this company's published financials from annual reports and NGX disclosures. State the year and source of any figures you recall."""

    prompt = f"""You are a senior investment analyst at a Nigerian SEC-regulated asset management firm. Analyze {name} ({ticker}), sector: {sector}, listed on NGX.

{data_section}

Provide analysis in this format:

COMPANY OVERVIEW
[2-3 sentences about the company]

FINANCIAL HEALTH
[Assessment with specific figures and source year]

VALUATION
[P/E assessment vs NGX peers]

KEY METRICS SUMMARY
- P/E Ratio: [value or N/A]
- EPS: [value or N/A]
- Revenue: [value or N/A]
- Net Profit: [value or N/A]
- ROE: [value or N/A]
- Debt/Equity: [value or N/A]

KEY RISKS
• [Risk 1]
• [Risk 2]
• [Risk 3]

RECOMMENDATION: BUY / HOLD / SELL
[One sentence rationale]

RISK SCORE: LOW / MEDIUM / HIGH
[One sentence]

DATA NOTE: [State data source - uploaded or training knowledge, and year]"""

    return await call_ai(prompt)

async def analyze_portfolio(name: str, holdings: list, metrics: dict) -> str:
    holdings_text = "\n".join([f"- {h['ticker']}: qty {h.get('quantity', 0)}, cost ₦{h.get('cost_price', 0)}" for h in holdings])
    prompt = f"""You are a senior portfolio manager at a Nigerian SEC-regulated asset management firm.

Portfolio: {name}
YTD Return: {metrics.get('ytd', 'N/A')}%
Holdings:
{holdings_text}

PORTFOLIO OVERVIEW
[2-3 sentences]

DIVERSIFICATION ASSESSMENT
[Sector concentration analysis]

KEY RISKS
• [Risk 1]
• [Risk 2]
• [Risk 3]

REBALANCING SUGGESTIONS
[Specific suggestions]"""
    return await call_ai(prompt)
