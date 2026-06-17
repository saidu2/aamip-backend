from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routers import auth, stocks, portfolios, market, uploads, ai, scraper

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AAMIP API",
    description="Asset Management Intelligence Platform — API",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router,       prefix="/api/v1")
app.include_router(stocks.router,     prefix="/api/v1")
app.include_router(portfolios.router, prefix="/api/v1")
app.include_router(market.router,     prefix="/api/v1")
app.include_router(uploads.router,    prefix="/api/v1")
app.include_router(ai.router,         prefix="/api/v1")
app.include_router(scraper.router,    prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "AAMIP API is running", "version": "1.0.0", "environment": settings.ENVIRONMENT}

@app.get("/health")
def health():
    return {"status": "ok"}
