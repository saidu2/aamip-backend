from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.security import get_current_user
from app.utils.helpers import log_action
from app.services import csv_service
import json

router = APIRouter(prefix="/uploads", tags=["Uploads"])

@router.post("/market-prices")
async def upload_market_prices(
    file: UploadFile = File(...),
    mapping: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    content = await file.read()
    mapping_dict = json.loads(mapping)
    result = csv_service.import_market_prices(db, content, file.filename, mapping_dict)
    log_action(db, current_user, "Uploaded market prices CSV", target=file.filename)
    return {"message": "Upload successful", **result}

@router.post("/company-financials")
async def upload_financials(
    file: UploadFile = File(...),
    mapping: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    content = await file.read()
    mapping_dict = json.loads(mapping)
    result = csv_service.import_company_financials(db, content, file.filename, mapping_dict)
    log_action(db, current_user, "Uploaded company financials CSV", target=file.filename)
    return {"message": "Upload successful", **result}

@router.post("/fx-rates")
async def upload_fx_rates(
    file: UploadFile = File(...),
    mapping: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    content = await file.read()
    mapping_dict = json.loads(mapping)
    result = csv_service.import_fx_rates(db, content, file.filename, mapping_dict)
    log_action(db, current_user, "Uploaded FX rates CSV", target=file.filename)
    return {"message": "Upload successful", **result}

@router.post("/macro-indicators")
async def upload_macro(
    file: UploadFile = File(...),
    mapping: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    content = await file.read()
    mapping_dict = json.loads(mapping)
    result = csv_service.import_macro_indicators(db, content, file.filename, mapping_dict)
    log_action(db, current_user, "Uploaded macro indicators CSV", target=file.filename)
    return {"message": "Upload successful", **result}

@router.post("/portfolio-holdings")
async def upload_holdings(
    file: UploadFile = File(...),
    mapping: str = Form(...),
    portfolio_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    content = await file.read()
    mapping_dict = json.loads(mapping)
    result = csv_service.import_portfolio_holdings(db, content, file.filename, mapping_dict, portfolio_id)
    log_action(db, current_user, "Uploaded portfolio holdings CSV", target=file.filename)
    return {"message": "Upload successful", **result}
