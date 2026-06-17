from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.utils.security import get_current_user, require_roles
from app.utils.helpers import log_action
from app.services.scraper_service import scrape_ngx_prices, save_prices_to_db

router = APIRouter(prefix="/scraper", tags=["Scraper"])

@router.post("/run")
async def run_scraper(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin", "analyst"))
):
    """Manually trigger NGX price scraper."""
    async def do_scrape():
        prices = await scrape_ngx_prices()
        saved  = save_prices_to_db(db, prices)
        log_action(db, current_user, f"NGX scraper ran — {saved} prices saved")

    background_tasks.add_task(do_scrape)
    return {"message": "NGX scraper started in background. Check Market Intelligence in 30 seconds."}

@router.get("/status")
def scraper_status(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Check when scraper last ran."""
    from app.models.stock import StockPrice
    from sqlalchemy import func
    latest = db.query(func.max(StockPrice.date)).scalar()
    count  = db.query(func.count(StockPrice.id)).scalar()
    return {
        "last_price_date": str(latest) if latest else None,
        "total_price_records": count,
        "today": str(date.today()),
        "is_current": str(latest) == str(date.today()) if latest else False,
    }
