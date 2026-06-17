"""
Run this once after setting up the database:
    python seed.py
"""
from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.stock import Stock
from app.utils.security import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# ── Default Users ─────────────────────────────────────────────────────────────
users = [
    {"full_name": "System Admin",      "email": "admin@aamip.com",      "password": "aamip2025", "role": UserRole.admin},
    {"full_name": "Ibrahim Musa",       "email": "analyst@aamip.com",    "password": "aamip2025", "role": UserRole.analyst},
    {"full_name": "Aisha Bello",        "email": "pm@aamip.com",         "password": "aamip2025", "role": UserRole.portfolio_manager},
    {"full_name": "Compliance Officer", "email": "compliance@aamip.com", "password": "aamip2025", "role": UserRole.compliance},
    {"full_name": "Executive User",     "email": "exec@aamip.com",       "password": "aamip2025", "role": UserRole.executive},
]

for u in users:
    existing = db.query(User).filter(User.email == u["email"]).first()
    if not existing:
        db.add(User(
            full_name=u["full_name"],
            email=u["email"],
            password=hash_password(u["password"]),
            role=u["role"],
            firm="Prime Capital & Investment Ltd",
        ))
        print(f"  Created user: {u['email']}")
    else:
        print(f"  Already exists: {u['email']}")

# ── NGX Stocks ────────────────────────────────────────────────────────────────
stocks = [
    {"ticker": "GTCO",    "name": "Guaranty Trust Holding Co.",     "sector": "Banking"},
    {"ticker": "ZENITH",  "name": "Zenith Bank Plc",                 "sector": "Banking"},
    {"ticker": "FBNH",    "name": "FBN Holdings Plc",                "sector": "Banking"},
    {"ticker": "UBA",     "name": "United Bank for Africa Plc",      "sector": "Banking"},
    {"ticker": "ACCESS",  "name": "Access Holdings Plc",             "sector": "Banking"},
    {"ticker": "DANGCEM", "name": "Dangote Cement Plc",              "sector": "Industrial Goods"},
    {"ticker": "BUACEMENT","name": "BUA Cement Plc",                 "sector": "Industrial Goods"},
    {"ticker": "MTNN",    "name": "MTN Nigeria Communications Plc",  "sector": "ICT"},
    {"ticker": "AIRTELAF","name": "Airtel Africa Plc",               "sector": "ICT"},
    {"ticker": "NESTLE",  "name": "Nestle Nigeria Plc",              "sector": "Consumer Goods"},
    {"ticker": "BUAFOOD", "name": "BUA Foods Plc",                   "sector": "Consumer Goods"},
    {"ticker": "NB",      "name": "Nigerian Breweries Plc",          "sector": "Consumer Goods"},
    {"ticker": "SEPLAT",  "name": "Seplat Energy Plc",               "sector": "Oil & Gas"},
    {"ticker": "TOTAL",   "name": "TotalEnergies Marketing Nigeria",  "sector": "Oil & Gas"},
    {"ticker": "OANDO",   "name": "Oando Plc",                       "sector": "Oil & Gas"},
    {"ticker": "WAPCO",   "name": "Lafarge Africa Plc",              "sector": "Industrial Goods"},
    {"ticker": "STANBIC", "name": "Stanbic IBTC Holdings Plc",       "sector": "Banking"},
    {"ticker": "TRANSCORP","name": "Transnational Corporation Plc",  "sector": "Conglomerates"},
]

for s in stocks:
    existing = db.query(Stock).filter(Stock.ticker == s["ticker"]).first()
    if not existing:
        db.add(Stock(ticker=s["ticker"], name=s["name"], sector=s["sector"]))
        print(f"  Created stock: {s['ticker']}")
    else:
        print(f"  Already exists: {s['ticker']}")

db.commit()
db.close()
print("\n✅ Seed complete. Default password for all users: aamip2025")
