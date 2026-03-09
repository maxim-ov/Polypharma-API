from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.db_models import User, DrugLog
from auth import get_current_user
from models.schemas import DrugLogCreate, DrugLogUpdate, DrugLogResponse, MessageResponse


router = APIRouter(prefix="/drug-logs", tags=["Drug Logs"])


@router.post("/", response_model=DrugLogResponse, status_code=status.HTTP_201_CREATED)
async def add_drug_log(
    log: DrugLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Log a drug the user has taken (with dosage and date-time)."""
    new_log = DrugLog(
        user_id=current_user.id,
        drug_name=log.drug_name,
        dosage=log.dosage,
        datetime=log.datetime,
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log


@router.get("/", response_model=List[DrugLogResponse])
async def get_drug_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve all drug logs for the authenticated user."""
    logs = db.query(DrugLog).filter(DrugLog.user_id == current_user.id).all()
    return logs


@router.put("/{log_id}", response_model=DrugLogResponse)
async def update_drug_log(
    log_id: int, 
    log: DrugLogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing drug log entry."""
    db_log = db.query(DrugLog).filter(DrugLog.id == log_id, DrugLog.user_id == current_user.id).first()
    if not db_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drug log not found")
    
    if log.drug_name is not None:
        db_log.drug_name = log.drug_name
    if log.dosage is not None:
        db_log.dosage = log.dosage
    if log.datetime is not None:
        db_log.datetime = log.datetime

    db.commit()
    db.refresh(db_log)
    return db_log


@router.delete("/{log_id}", response_model=MessageResponse)
async def delete_drug_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a drug log entry."""
    db_log = db.query(DrugLog).filter(DrugLog.id == log_id, DrugLog.user_id == current_user.id).first()
    if not db_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drug log not found")
    
    db.delete(db_log)
    db.commit()
    return MessageResponse(message=f"Drug log {log_id} deleted successfully.")
