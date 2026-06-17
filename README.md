# AAMIP Backend

FastAPI backend for the Asset Management Intelligence Platform.

## Setup

### 1. Install PostgreSQL
Download and install PostgreSQL from https://www.postgresql.org/download/windows/
- During install, set password to: `password` (or update DATABASE_URL in .env)
- Default port: 5432

### 2. Create the database
Open pgAdmin or psql and run:
```sql
CREATE DATABASE aamip;
```

### 3. Create virtual environment
```bash
cd aamip-backend
python -m venv venv
venv\Scripts\activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Set up environment variables
```bash
copy .env.example .env
```
Edit `.env` with your database password and Gemini API key.

### 6. Seed the database
```bash
python seed.py
```

### 7. Run the server
```bash
uvicorn app.main:app --reload --port 8001
```

API docs available at: http://localhost:8001/docs

## Default Login Credentials
| Email | Password | Role |
|-------|----------|------|
| admin@aamip.com | aamip2025 | Admin |
| analyst@aamip.com | aamip2025 | Analyst |
| pm@aamip.com | aamip2025 | Portfolio Manager |
| compliance@aamip.com | aamip2025 | Compliance |
| exec@aamip.com | aamip2025 | Executive |

## API Endpoints
- `POST /api/v1/auth/login` — Login
- `GET  /api/v1/stocks` — List all stocks
- `GET  /api/v1/portfolios` — List portfolios
- `GET  /api/v1/portfolios/{id}/holdings` — Get portfolio holdings with P&L
- `GET  /api/v1/market/fx-rates` — FX rates
- `GET  /api/v1/market/macro` — Macro indicators
- `POST /api/v1/uploads/market-prices` — Upload NGX price CSV
- `POST /api/v1/uploads/company-financials` — Upload financials CSV
- `POST /api/v1/ai/analyze-stock` — Run AI stock analysis
- `POST /api/v1/ai/analyze-portfolio` — Run AI portfolio analysis

Full interactive docs: http://localhost:8001/docs
