import pandas as pd
from io import BytesIO
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.stock import StockPrice, StockFinancial, Stock
from app.models.market import FXRate, MacroIndicator
from app.models.portfolio import Holding

def parse_date(val):
    if not val or pd.isna(val):
        return None
    if isinstance(val, datetime):
        return val.date()
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y'):
        try:
            return datetime.strptime(str(val).strip(), fmt).date()
        except:
            continue
    return None

def safe_float(val):
    try:
        if pd.isna(val):
            return None
        return float(str(val).replace(',', '').strip())
    except:
        return None

def read_file(file_bytes: bytes, filename: str) -> pd.DataFrame:
    if filename.endswith('.csv'):
        return pd.read_csv(BytesIO(file_bytes))
    else:
        return pd.read_excel(BytesIO(file_bytes))

# ── Market Prices ─────────────────────────────────────────────────────────────
def import_market_prices(db: Session, file_bytes: bytes, filename: str, mapping: dict) -> dict:
    df = read_file(file_bytes, filename)
    df = df.rename(columns={v: k for k, v in mapping.items() if v})
    inserted = 0
    errors = []

    for _, row in df.iterrows():
        try:
            date = parse_date(row.get('date'))
            ticker = str(row.get('ticker', '')).strip().upper()
            close_price = safe_float(row.get('close_price'))
            if not date or not ticker or close_price is None:
                continue
            existing = db.query(StockPrice).filter(StockPrice.ticker == ticker, StockPrice.date == date).first()
            if existing:
                existing.close_price = close_price
                existing.open_price  = safe_float(row.get('open_price'))
                existing.high_price  = safe_float(row.get('high_price'))
                existing.low_price   = safe_float(row.get('low_price'))
                existing.volume      = safe_float(row.get('volume'))
            else:
                db.add(StockPrice(
                    ticker=ticker, date=date, close_price=close_price,
                    open_price=safe_float(row.get('open_price')),
                    high_price=safe_float(row.get('high_price')),
                    low_price=safe_float(row.get('low_price')),
                    volume=safe_float(row.get('volume')),
                ))
                inserted += 1
        except Exception as e:
            errors.append(str(e))

    db.commit()
    return {"inserted": inserted, "errors": len(errors)}

# ── Company Financials ────────────────────────────────────────────────────────
def import_company_financials(db: Session, file_bytes: bytes, filename: str, mapping: dict) -> dict:
    df = read_file(file_bytes, filename)
    df = df.rename(columns={v: k for k, v in mapping.items() if v})
    inserted = 0

    for _, row in df.iterrows():
        try:
            ticker = str(row.get('ticker', '')).strip().upper()
            year   = int(safe_float(row.get('year')) or 0)
            if not ticker or not year:
                continue
            existing = db.query(StockFinancial).filter(StockFinancial.ticker == ticker, StockFinancial.year == year).first()
            if existing:
                existing.revenue    = safe_float(row.get('revenue'))
                existing.net_profit = safe_float(row.get('net_profit'))
                existing.eps        = safe_float(row.get('eps'))
            else:
                db.add(StockFinancial(
                    ticker=ticker, year=year,
                    revenue=safe_float(row.get('revenue')),
                    net_profit=safe_float(row.get('net_profit')),
                    eps=safe_float(row.get('eps')),
                    total_assets=safe_float(row.get('total_assets')),
                    total_equity=safe_float(row.get('total_equity')),
                    total_debt=safe_float(row.get('total_debt')),
                ))
                inserted += 1
        except Exception as e:
            pass

    db.commit()
    return {"inserted": inserted}

# ── FX Rates ──────────────────────────────────────────────────────────────────
def import_fx_rates(db: Session, file_bytes: bytes, filename: str, mapping: dict) -> dict:
    df = read_file(file_bytes, filename)
    df = df.rename(columns={v: k for k, v in mapping.items() if v})
    inserted = 0

    for _, row in df.iterrows():
        try:
            date = parse_date(row.get('date'))
            if not date:
                continue
            existing = db.query(FXRate).filter(FXRate.date == date).first()
            if existing:
                existing.usd_ngn = safe_float(row.get('usd_ngn'))
                existing.gbp_ngn = safe_float(row.get('gbp_ngn'))
                existing.eur_ngn = safe_float(row.get('eur_ngn'))
            else:
                db.add(FXRate(
                    date=date,
                    usd_ngn=safe_float(row.get('usd_ngn')),
                    gbp_ngn=safe_float(row.get('gbp_ngn')),
                    eur_ngn=safe_float(row.get('eur_ngn')),
                ))
                inserted += 1
        except:
            pass

    db.commit()
    return {"inserted": inserted}

# ── Macro Indicators ──────────────────────────────────────────────────────────
def import_macro_indicators(db: Session, file_bytes: bytes, filename: str, mapping: dict) -> dict:
    df = read_file(file_bytes, filename)
    df = df.rename(columns={v: k for k, v in mapping.items() if v})
    inserted = 0

    for _, row in df.iterrows():
        try:
            date      = parse_date(row.get('date'))
            indicator = str(row.get('indicator', '')).strip()
            value     = safe_float(row.get('value'))
            if not date or not indicator or value is None:
                continue
            db.add(MacroIndicator(
                date=date, indicator=indicator, value=value,
                source=str(row.get('source', '')).strip() or None,
            ))
            inserted += 1
        except:
            pass

    db.commit()
    return {"inserted": inserted}

# ── Portfolio Holdings ────────────────────────────────────────────────────────
def import_portfolio_holdings(db: Session, file_bytes: bytes, filename: str, mapping: dict, portfolio_id: int) -> dict:
    df = read_file(file_bytes, filename)
    df = df.rename(columns={v: k for k, v in mapping.items() if v})
    inserted = 0

    for _, row in df.iterrows():
        try:
            ticker     = str(row.get('ticker', '')).strip().upper()
            quantity   = safe_float(row.get('quantity'))
            cost_price = safe_float(row.get('cost_price'))
            if not ticker or quantity is None or cost_price is None:
                continue
            db.add(Holding(
                portfolio_id=portfolio_id,
                ticker=ticker,
                quantity=quantity,
                cost_price=cost_price,
                purchase_date=parse_date(row.get('purchase_date')),
            ))
            inserted += 1
        except:
            pass

    db.commit()
    return {"inserted": inserted}
