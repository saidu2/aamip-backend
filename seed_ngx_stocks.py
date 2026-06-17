"""
Seed all major NGX listed companies.
Run: python seed_ngx_stocks.py
"""
from app.database import SessionLocal, engine, Base
from app.models.stock import Stock, Recommendation, RiskLevel

Base.metadata.create_all(bind=engine)
db = SessionLocal()

NGX_STOCKS = [
    # Banking
    {"ticker": "GTCO",      "name": "Guaranty Trust Holding Co. Plc",       "sector": "Banking"},
    {"ticker": "ZENITH",    "name": "Zenith Bank Plc",                        "sector": "Banking"},
    {"ticker": "FBNH",      "name": "FBN Holdings Plc",                       "sector": "Banking"},
    {"ticker": "UBA",       "name": "United Bank for Africa Plc",             "sector": "Banking"},
    {"ticker": "ACCESS",    "name": "Access Holdings Plc",                    "sector": "Banking"},
    {"ticker": "STANBIC",   "name": "Stanbic IBTC Holdings Plc",              "sector": "Banking"},
    {"ticker": "FCMB",      "name": "FCMB Group Plc",                         "sector": "Banking"},
    {"ticker": "ETI",       "name": "Ecobank Transnational Incorporated",     "sector": "Banking"},
    {"ticker": "FIDELITYBK","name": "Fidelity Bank Plc",                      "sector": "Banking"},
    {"ticker": "STERLINBN", "name": "Sterling Financial Holdings Plc",        "sector": "Banking"},
    {"ticker": "WEMABANK",  "name": "Wema Bank Plc",                          "sector": "Banking"},
    {"ticker": "UNIONBANK", "name": "Union Bank of Nigeria Plc",              "sector": "Banking"},
    {"ticker": "JAIZBANK",  "name": "Jaiz Bank Plc",                          "sector": "Banking"},
    {"ticker": "ABBEYBDS",  "name": "Abbey Mortgage Bank Plc",                "sector": "Banking"},

    # Insurance
    {"ticker": "AIICO",     "name": "AIICO Insurance Plc",                    "sector": "Insurance"},
    {"ticker": "MANSARD",   "name": "AXA Mansard Insurance Plc",              "sector": "Insurance"},
    {"ticker": "CUSTODIAN", "name": "Custodian Investment Plc",               "sector": "Insurance"},
    {"ticker": "LASACO",    "name": "Lasaco Assurance Plc",                   "sector": "Insurance"},
    {"ticker": "LINKASSURE","name": "Linkage Assurance Plc",                  "sector": "Insurance"},
    {"ticker": "NEM",       "name": "NEM Insurance Plc",                      "sector": "Insurance"},
    {"ticker": "CORNERST",  "name": "Cornerstone Insurance Plc",              "sector": "Insurance"},
    {"ticker": "SOVEREIGNINS","name": "Sovereign Trust Insurance Plc",        "sector": "Insurance"},

    # Oil & Gas
    {"ticker": "SEPLAT",    "name": "Seplat Energy Plc",                      "sector": "Oil & Gas"},
    {"ticker": "TOTAL",     "name": "TotalEnergies Marketing Nigeria Plc",    "sector": "Oil & Gas"},
    {"ticker": "OANDO",     "name": "Oando Plc",                              "sector": "Oil & Gas"},
    {"ticker": "ARDOVA",    "name": "Ardova Plc",                             "sector": "Oil & Gas"},
    {"ticker": "ARADEL",    "name": "Aradel Holdings Plc",                    "sector": "Oil & Gas"},
    {"ticker": "EROTON",    "name": "Eroton Exploration and Production Plc",  "sector": "Oil & Gas"},
    {"ticker": "CONOIL",    "name": "Conoil Plc",                             "sector": "Oil & Gas"},
    {"ticker": "ETERNA",    "name": "Eterna Plc",                             "sector": "Oil & Gas"},
    {"ticker": "MRS",       "name": "MRS Oil Nigeria Plc",                    "sector": "Oil & Gas"},

    # Consumer Goods
    {"ticker": "NESTLE",    "name": "Nestle Nigeria Plc",                     "sector": "Consumer Goods"},
    {"ticker": "BUAFOOD",   "name": "BUA Foods Plc",                          "sector": "Consumer Goods"},
    {"ticker": "NB",        "name": "Nigerian Breweries Plc",                 "sector": "Consumer Goods"},
    {"ticker": "GUINNESS",  "name": "Guinness Nigeria Plc",                   "sector": "Consumer Goods"},
    {"ticker": "FLOURMILL", "name": "Flour Mills of Nigeria Plc",             "sector": "Consumer Goods"},
    {"ticker": "DANGSUGAR", "name": "Dangote Sugar Refinery Plc",             "sector": "Consumer Goods"},
    {"ticker": "CADBURY",   "name": "Cadbury Nigeria Plc",                    "sector": "Consumer Goods"},
    {"ticker": "HONYFLOUR", "name": "Honeywell Flour Mill Plc",               "sector": "Consumer Goods"},
    {"ticker": "CHAMPION",  "name": "Champion Breweries Plc",                 "sector": "Consumer Goods"},
    {"ticker": "INTBREW",   "name": "International Breweries Plc",            "sector": "Consumer Goods"},
    {"ticker": "PRESCO",    "name": "Presco Plc",                             "sector": "Consumer Goods"},
    {"ticker": "OKOMUOIL",  "name": "Okomu Oil Palm Company Plc",             "sector": "Consumer Goods"},

    # Industrial Goods
    {"ticker": "DANGCEM",   "name": "Dangote Cement Plc",                     "sector": "Industrial Goods"},
    {"ticker": "BUACEMENT", "name": "BUA Cement Plc",                         "sector": "Industrial Goods"},
    {"ticker": "WAPCO",     "name": "Lafarge Africa Plc",                     "sector": "Industrial Goods"},
    {"ticker": "BERGER",    "name": "Berger Paints Nigeria Plc",              "sector": "Industrial Goods"},
    {"ticker": "CAPGREEN",  "name": "CAP Plc",                                "sector": "Industrial Goods"},
    {"ticker": "PORTPAINT", "name": "Portland Paints and Products Plc",       "sector": "Industrial Goods"},
    {"ticker": "CUTIX",     "name": "Cutix Plc",                              "sector": "Industrial Goods"},
    {"ticker": "DEAPCAP",   "name": "Deap Capital Management & Trust Plc",    "sector": "Industrial Goods"},

    # ICT / Technology
    {"ticker": "MTNN",      "name": "MTN Nigeria Communications Plc",         "sector": "ICT"},
    {"ticker": "AIRTELAF",  "name": "Airtel Africa Plc",                      "sector": "ICT"},
    {"ticker": "CWG",       "name": "CWG Plc",                                "sector": "ICT"},
    {"ticker": "ETRANZACT", "name": "eTranzact International Plc",            "sector": "ICT"},
    {"ticker": "CHAMS",     "name": "Chams Holding Company Plc",              "sector": "ICT"},
    {"ticker": "OMATEK",    "name": "Omatek Ventures Plc",                    "sector": "ICT"},

    # Healthcare
    {"ticker": "GLAXOSMITH","name": "GlaxoSmithKline Consumer Nigeria Plc",   "sector": "Healthcare"},
    {"ticker": "FIDSON",    "name": "Fidson Healthcare Plc",                  "sector": "Healthcare"},
    {"ticker": "MAYBAKER",  "name": "May & Baker Nigeria Plc",                "sector": "Healthcare"},
    {"ticker": "NEIMETH",   "name": "Neimeth International Pharmaceuticals",  "sector": "Healthcare"},
    {"ticker": "PHARMDEKO", "name": "Pharma-Deko Plc",                        "sector": "Healthcare"},
    {"ticker": "MORISON",   "name": "Morison Industries Plc",                 "sector": "Healthcare"},

    # Conglomerates
    {"ticker": "TRANSCORP", "name": "Transnational Corporation Plc",          "sector": "Conglomerates"},
    {"ticker": "UACN",      "name": "UAC of Nigeria Plc",                     "sector": "Conglomerates"},
    {"ticker": "JOHNHOLT",  "name": "John Holt Plc",                          "sector": "Conglomerates"},

    # Real Estate
    {"ticker": "UPDC",      "name": "UPDC Plc",                               "sector": "Real Estate"},
    {"ticker": "REGALINS",  "name": "Regal Insurance Plc",                    "sector": "Real Estate"},

    # Agriculture
    {"ticker": "LIVESTOCK", "name": "Livestock Feeds Plc",                    "sector": "Agriculture"},
    {"ticker": "NOTORE",    "name": "Notore Chemical Industries Plc",         "sector": "Agriculture"},
    {"ticker": "VANLEER",   "name": "Van Leer Containers Nigeria Plc",        "sector": "Agriculture"},

    # Services
    {"ticker": "TRANSCOHOT","name": "Transcorp Hotels Plc",                   "sector": "Services"},
    {"ticker": "TANTALIZER","name": "Tantalizers Plc",                        "sector": "Services"},
    {"ticker": "ROYALEX",   "name": "Royalex Plc",                            "sector": "Services"},
    {"ticker": "RTBRISCOE", "name": "R.T. Briscoe Nigeria Plc",               "sector": "Services"},

    # Utilities
    {"ticker": "GEREGU",    "name": "Geregu Power Plc",                       "sector": "Utilities"},
    {"ticker": "TRANSEXPR", "name": "Trans Nationwide Express Plc",           "sector": "Utilities"},
]

inserted = 0
skipped  = 0

for s in NGX_STOCKS:
    existing = db.query(Stock).filter(Stock.ticker == s["ticker"]).first()
    if not existing:
        db.add(Stock(
            ticker     = s["ticker"],
            name       = s["name"],
            sector     = s["sector"],
            recommendation = Recommendation.HOLD,
            risk_level     = RiskLevel.MEDIUM,
        ))
        inserted += 1
        print(f"  + {s['ticker']} — {s['name']}")
    else:
        skipped += 1

db.commit()
db.close()

print(f"\n✅ Done! {inserted} new stocks added, {skipped} already existed")
print(f"   Total NGX stocks in database: {inserted + skipped}")
