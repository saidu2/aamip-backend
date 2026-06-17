"""
Seed realistic market data for development.
Run: python seed_market_data.py
"""
from datetime import date, timedelta
import random
from app.database import SessionLocal, engine, Base
from app.models.stock import StockPrice
from app.models.market import FXRate, MacroIndicator

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# ── Realistic NGX closing prices (as of early 2025) ───────────────────────────
STOCK_PRICES = {
    "GTCO":     {"base": 47.20,  "vol": 0.02},
    "ZENITH":   {"base": 34.80,  "vol": 0.02},
    "FBNH":     {"base": 22.10,  "vol": 0.025},
    "UBA":      {"base": 24.50,  "vol": 0.02},
    "ACCESS":   {"base": 19.80,  "vol": 0.022},
    "DANGCEM":  {"base": 372.00, "vol": 0.015},
    "BUACEMENT":{"base": 95.00,  "vol": 0.018},
    "MTNN":     {"base": 198.50, "vol": 0.018},
    "AIRTELAF": {"base": 2150.0, "vol": 0.02},
    "NESTLE":   {"base": 920.00, "vol": 0.012},
    "BUAFOOD":  {"base": 148.00, "vol": 0.02},
    "NB":       {"base": 32.50,  "vol": 0.018},
    "SEPLAT":   {"base": 4200.0, "vol": 0.025},
    "TOTAL":    {"base": 310.00, "vol": 0.02},
    "OANDO":    {"base": 9.80,   "vol": 0.03},
    "WAPCO":    {"base": 41.50,  "vol": 0.02},
    "STANBIC":  {"base": 62.00,  "vol": 0.018},
    "TRANSCORP":{"base": 14.20,  "vol": 0.025},
}

# Generate 60 days of price history
today = date.today()
inserted = 0

print("Seeding stock prices...")
for ticker, config in STOCK_PRICES.items():
    price = config["base"]
    for i in range(59, -1, -1):
        price_date = today - timedelta(days=i)
        # Skip weekends
        if price_date.weekday() >= 5:
            continue

        # Random walk
        change = random.gauss(0.001, config["vol"])
        price  = round(price * (1 + change), 2)
        price  = max(price, config["base"] * 0.5)  # floor at 50% of base

        existing = db.query(StockPrice).filter(
            StockPrice.ticker == ticker,
            StockPrice.date   == price_date
        ).first()

        if not existing:
            open_p  = round(price * random.uniform(0.98, 1.02), 2)
            high_p  = round(max(price, open_p) * random.uniform(1.001, 1.02), 2)
            low_p   = round(min(price, open_p) * random.uniform(0.98, 0.999), 2)
            volume  = round(random.uniform(500000, 10000000))

            db.add(StockPrice(
                ticker      = ticker,
                date        = price_date,
                close_price = price,
                open_price  = open_p,
                high_price  = high_p,
                low_price   = low_p,
                volume      = volume,
            ))
            inserted += 1

db.commit()
print(f"  {inserted} price records inserted")

# ── FX Rates ──────────────────────────────────────────────────────────────────
print("Seeding FX rates...")
fx_inserted = 0
usd_ngn = 1580.0

for i in range(59, -1, -1):
    rate_date = today - timedelta(days=i)
    if rate_date.weekday() >= 5:
        continue

    usd_ngn = round(usd_ngn + random.gauss(2, 8), 2)
    usd_ngn = max(1400, min(1800, usd_ngn))

    existing = db.query(FXRate).filter(FXRate.date == rate_date).first()
    if not existing:
        db.add(FXRate(
            date    = rate_date,
            usd_ngn = usd_ngn,
            gbp_ngn = round(usd_ngn * 1.27, 2),
            eur_ngn = round(usd_ngn * 1.09, 2),
        ))
        fx_inserted += 1

db.commit()
print(f"  {fx_inserted} FX rate records inserted")

# ── Macro Indicators ──────────────────────────────────────────────────────────
print("Seeding macro indicators...")
macro_data = [
    {"indicator": "Inflation Rate",       "value": 31.70, "source": "NBS"},
    {"indicator": "MPR (CBN)",            "value": 26.75, "source": "CBN"},
    {"indicator": "T-Bill Rate (91-day)", "value": 18.50, "source": "CBN"},
    {"indicator": "T-Bill Rate (182-day)","value": 19.20, "source": "CBN"},
    {"indicator": "T-Bill Rate (364-day)","value": 20.10, "source": "CBN"},
    {"indicator": "GDP Growth Rate",      "value": 3.46,  "source": "NBS"},
    {"indicator": "USD/NGN Rate",         "value": 1580.0,"source": "CBN"},
]

macro_inserted = 0
for m in macro_data:
    existing = db.query(MacroIndicator).filter(
        MacroIndicator.indicator == m["indicator"],
        MacroIndicator.date      == today
    ).first()
    if not existing:
        db.add(MacroIndicator(
            date      = today,
            indicator = m["indicator"],
            value     = m["value"],
            source    = m["source"],
        ))
        macro_inserted += 1

db.commit()
print(f"  {macro_inserted} macro indicators inserted")

db.close()
print("\n✅ Market data seed complete!")
print(f"   Stock prices: {inserted} records across {len(STOCK_PRICES)} tickers")
print(f"   FX rates:     {fx_inserted} records")
print(f"   Macro data:   {macro_inserted} indicators")
