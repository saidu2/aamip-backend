"""
NGX Market Data Scraper
Fetches daily stock prices from NGX website automatically.
Falls back gracefully if the site is unavailable or layout changes.
"""
import httpx
import re
from datetime import date, datetime
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from app.models.stock import StockPrice, Stock

NGX_EQUITIES_URL = "https://ngxgroup.com/exchange/data/equities-price-list/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

def clean_number(val: str) -> float | None:
    if not val:
        return None
    try:
        return float(str(val).replace(",", "").replace("₦", "").strip())
    except:
        return None

async def scrape_ngx_prices() -> list[dict]:
    """
    Scrape NGX equity prices.
    Returns list of dicts: { ticker, close_price, open_price, high_price, low_price, volume }
    Returns empty list if scraping fails.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0, headers=HEADERS, follow_redirects=True) as client:
            res = await client.get(NGX_EQUITIES_URL)
            if res.status_code != 200:
                print(f"NGX scraper: HTTP {res.status_code}")
                return []

        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.find("table")
        if not table:
            print("NGX scraper: No table found on page")
            return []

        rows = table.find_all("tr")
        if len(rows) < 2:
            return []

        # Find header to detect column positions
        headers = [th.get_text(strip=True).lower() for th in rows[0].find_all(["th", "td"])]

        def col(name_hints: list[str]) -> int:
            for hint in name_hints:
                for i, h in enumerate(headers):
                    if hint in h:
                        return i
            return -1

        ticker_col = col(["symbol", "ticker", "code"])
        close_col  = col(["close", "last price", "price"])
        open_col   = col(["open"])
        high_col   = col(["high"])
        low_col    = col(["low"])
        vol_col    = col(["volume", "vol"])

        if ticker_col == -1 or close_col == -1:
            print(f"NGX scraper: Could not find required columns. Headers: {headers}")
            return []

        results = []
        for row in rows[1:]:
            cells = row.find_all(["td", "th"])
            if len(cells) <= max(ticker_col, close_col):
                continue
            ticker = cells[ticker_col].get_text(strip=True).upper()
            close  = clean_number(cells[close_col].get_text(strip=True))
            if not ticker or not close:
                continue
            results.append({
                "ticker":      ticker,
                "close_price": close,
                "open_price":  clean_number(cells[open_col].get_text(strip=True)) if open_col >= 0 and len(cells) > open_col else None,
                "high_price":  clean_number(cells[high_col].get_text(strip=True)) if high_col >= 0 and len(cells) > high_col else None,
                "low_price":   clean_number(cells[low_col].get_text(strip=True))  if low_col  >= 0 and len(cells) > low_col  else None,
                "volume":      clean_number(cells[vol_col].get_text(strip=True))  if vol_col  >= 0 and len(cells) > vol_col  else None,
            })

        print(f"NGX scraper: {len(results)} stocks scraped successfully")
        return results

    except Exception as e:
        print(f"NGX scraper error: {e}")
        return []

def save_prices_to_db(db: Session, prices: list[dict], price_date: date = None) -> int:
    """Save scraped prices to database. Returns number of records saved."""
    if not prices:
        return 0

    today = price_date or date.today()
    saved = 0

    for p in prices:
        try:
            existing = db.query(StockPrice).filter(
                StockPrice.ticker == p["ticker"],
                StockPrice.date   == today
            ).first()

            if existing:
                existing.close_price = p["close_price"]
                existing.open_price  = p.get("open_price")
                existing.high_price  = p.get("high_price")
                existing.low_price   = p.get("low_price")
                existing.volume      = p.get("volume")
            else:
                db.add(StockPrice(
                    ticker      = p["ticker"],
                    date        = today,
                    close_price = p["close_price"],
                    open_price  = p.get("open_price"),
                    high_price  = p.get("high_price"),
                    low_price   = p.get("low_price"),
                    volume      = p.get("volume"),
                ))
                saved += 1
        except Exception as e:
            print(f"Error saving {p.get('ticker')}: {e}")
            continue

    db.commit()
    return saved
