from fastapi import APIRouter
from typing import List
from models.schemas import DrugInteractionResponse

router = APIRouter(prefix="/interactions", tags=["Drug Interactions"])


@router.get("/major", response_model=List[DrugInteractionResponse])
async def get_major_interactions():
    """Get all major drug interactions for the authenticated user's logged drugs.
    These are drugs the user should NOT take.
    """
    # TODO: query interactions table where level = 'major'
    #       filtered to the user's logged drugs
    return []


@router.get("/moderate", response_model=List[DrugInteractionResponse])
async def get_moderate_interactions():
    """Get all moderate drug interactions for the authenticated user's logged drugs.
    These are drugs the user should be careful taking.
    """
    # TODO: query interactions table where level = 'moderate'
    #       filtered to the user's logged drugs
    return []


@router.get("/minor", response_model=List[DrugInteractionResponse])
async def get_minor_interactions():
    """Get all minor drug interactions for the authenticated user's logged drugs.
    These are drugs the user should be fine taking.
    """
    # TODO: query interactions table where level = 'minor'
    #       filtered to the user's logged drugs
    return []


@router.get("/safe", response_model=List[DrugInteractionResponse])
async def get_safe_interactions():
    """Get all drug pairs with no known interaction for the authenticated user's logged drugs.
    These are drugs with no recorded interaction.
    """
    # TODO: find drug pairs NOT present in the interactions table
    #       for the user's logged drugs
    return []
