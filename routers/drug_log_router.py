from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.db_models import User, DrugLog
from auth import get_current_user
from models.schemas import DrugLogCreate, DrugLogUpdate, DrugLogResponse, MessageResponse
from rxnorm import resolve_drug


router = APIRouter(prefix="/drug-logs", tags=["Drug Logs"])


@router.post("/", response_model=DrugLogResponse, status_code=status.HTTP_201_CREATED)
async def add_drug_log(
    log: DrugLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Log a drug the user has taken (with dosage and date-time)."""
    drug = resolve_drug(log.drug_name, db)
    if not drug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Drug '{log.drug_name}' not found in the database."
        )
    new_log = DrugLog(
        user_id=current_user.id,
        drug_id=drug.id,
        dosage=log.dosage,
        datetime=log.datetime,
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return DrugLogResponse(
        id=new_log.id,
        user_id=new_log.user_id,
        drug_id=new_log.drug_id,
        drug_name=new_log.drug.name,
        dosage=new_log.dosage,
        datetime=new_log.datetime,
    )


@router.get("/", response_model=List[DrugLogResponse])
async def get_drug_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve all drug logs for the authenticated user."""
    logs = db.query(DrugLog).filter(DrugLog.user_id == current_user.id).all()
    return [
        DrugLogResponse(
            id=log.id,
            user_id=log.user_id,
            drug_id=log.drug_id,
            drug_name=log.drug.name,
            dosage=log.dosage,
            datetime=log.datetime,
        )
        for log in logs
    ]


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
        drug = resolve_drug(log.drug_name, db)
        if not drug:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Drug '{log.drug_name}' not found in the database."
            )
        db_log.drug_id = drug.id
    if log.dosage is not None:
        db_log.dosage = log.dosage
    if log.datetime is not None:
        db_log.datetime = log.datetime

    db.commit()
    db.refresh(db_log)
    return DrugLogResponse(
        id=db_log.id,
        user_id=db_log.user_id,
        drug_id=db_log.drug_id,
        drug_name=db_log.drug.name,
        dosage=db_log.dosage,
        datetime=db_log.datetime,
    )


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
