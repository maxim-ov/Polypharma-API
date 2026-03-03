from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime
from models.schemas import DrugLogCreate, DrugLogUpdate, DrugLogResponse, MessageResponse

router = APIRouter(prefix="/drug-logs", tags=["Drug Logs"])


@router.post("/", response_model=DrugLogResponse, status_code=status.HTTP_201_CREATED)
async def add_drug_log(log: DrugLogCreate):
    """Log a drug the user has taken (with dosage and date-time)."""
    # TODO: get current user from JWT, persist to database
    return DrugLogResponse(
        id=1,
        user_id=1,
        drug_name=log.drug_name,
        dosage=log.dosage,
        datetime=log.datetime,
    )


@router.get("/", response_model=List[DrugLogResponse])
async def get_drug_logs():
    """Retrieve all drug logs for the authenticated user."""
    # TODO: fetch from database filtered by current user
    return []


@router.put("/{log_id}", response_model=DrugLogResponse)
async def update_drug_log(log_id: int, log: DrugLogUpdate):
    """Update an existing drug log entry."""
    # TODO: verify ownership, update in database
    return DrugLogResponse(
        id=log_id,
        user_id=1,
        drug_name=log.drug_name or "placeholder",
        dosage=log.dosage or "placeholder",
        datetime=log.datetime or datetime.now(),
    )


@router.delete("/{log_id}", response_model=MessageResponse)
async def delete_drug_log(log_id: int):
    """Remove a drug log entry."""
    # TODO: verify ownership, delete from database
    return MessageResponse(message=f"Drug log {log_id} deleted successfully.")
