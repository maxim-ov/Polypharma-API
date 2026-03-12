from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session

from models.schemas import DrugInteractionResponse
from database import get_db
from models.db_models import User, DrugLog, Drug, DrugInteraction
from auth import get_current_user


router = APIRouter(prefix="/interactions", tags=["Drug Interactions"])


def get_recent_drugs(db: Session, current_user: User):
    time_threshold = datetime.utcnow() - timedelta(days=1)
    recent_logs = db.query(DrugLog.drug_name).filter(
        DrugLog.user_id == current_user.id,
        DrugLog.datetime >= time_threshold
    ).all()
    recent_drug_names = [row[0] for row in recent_logs]
    
    if not recent_drug_names:
        return [], {}

    drug_records = db.query(Drug).filter(Drug.name.in_(recent_drug_names)).all()
    drug_ids = [d.id for d in drug_records]
    id_to_name = {d.id: d.name for d in drug_records}
    
    return drug_ids, id_to_name


def get_interactions_by_level(level: str, current_user: User, db: Session):
    drug_ids, id_to_name = get_recent_drugs(db, current_user)
    
    if len(drug_ids) < 2:
        return []

    interactions = db.query(DrugInteraction).filter(
        DrugInteraction.level.ilike(level),
        DrugInteraction.drug_a_id.in_(drug_ids),
        DrugInteraction.drug_b_id.in_(drug_ids)
    ).all()
    
    results = []
    seen = set()
    for interaction in interactions:
        name_a = id_to_name[interaction.drug_a_id]
        name_b = id_to_name[interaction.drug_b_id]
        pair = tuple(sorted([name_a, name_b]))
        if pair not in seen:
            seen.add(pair)
            results.append(DrugInteractionResponse(
                drug_a=name_a,
                drug_b=name_b,
                level=interaction.level,
                category=interaction.category
            ))
    return results


@router.get("/major", response_model=List[DrugInteractionResponse])
async def get_major_interactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all major drug interactions for the authenticated user's logged drugs.
    These are drugs the user should NOT take.
    """
    return get_interactions_by_level("major", current_user, db)


@router.get("/moderate", response_model=List[DrugInteractionResponse])
async def get_moderate_interactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all moderate drug interactions for the authenticated user's logged drugs.
    These are drugs the user should be careful taking.
    """
    return get_interactions_by_level("moderate", current_user, db)


@router.get("/minor", response_model=List[DrugInteractionResponse])
async def get_minor_interactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all minor drug interactions for the authenticated user's logged drugs.
    These are drugs the user should be fine taking.
    """
    return get_interactions_by_level("minor", current_user, db)


@router.get("/safe", response_model=List[DrugInteractionResponse])
async def get_safe_interactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all drug pairs with no known interaction for the authenticated user's logged drugs.
    These are drugs with no recorded interaction.
    """
    drug_ids, id_to_name = get_recent_drugs(db, current_user)
    
    if len(drug_ids) < 2:
        return []
        
    interactions = db.query(DrugInteraction).filter(
        DrugInteraction.drug_a_id.in_(drug_ids),
        DrugInteraction.drug_b_id.in_(drug_ids)
    ).all()
    
    unsafe_pairs = set()
    for ix in interactions:
        unsafe_pairs.add(tuple(sorted([ix.drug_a_id, ix.drug_b_id])))
        
    results = []
    seen = set()
    for i in range(len(drug_ids)):
        for j in range(i + 1, len(drug_ids)):
            id_a = drug_ids[i]
            id_b = drug_ids[j]
            pair = tuple(sorted([id_a, id_b]))
            if pair not in unsafe_pairs:
                name_a = id_to_name[id_a]
                name_b = id_to_name[id_b]
                name_pair = tuple(sorted([name_a, name_b]))
                if name_pair not in seen:
                    seen.add(name_pair)
                    results.append(DrugInteractionResponse(
                        drug_a=name_a,
                        drug_b=name_b,
                        level="safe",
                        category="None"
                    ))
    return results
