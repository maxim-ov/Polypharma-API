from pydantic import BaseModel, EmailStr, computed_field
from typing import Optional
from datetime import datetime


# ──────────────────────────────────────
# Auth schemas
# ──────────────────────────────────────

class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ──────────────────────────────────────
# Drug log schemas
# ──────────────────────────────────────

class DrugLogCreate(BaseModel):
    drug_name: str
    dosage: str
    datetime: datetime


class DrugLogUpdate(BaseModel):
    drug_name: Optional[str] = None
    dosage: Optional[str] = None
    datetime: Optional[datetime] = None


class DrugLogResponse(BaseModel):
    id: int
    user_id: int
    drug_id: str
    drug_name: str
    dosage: str
    datetime: datetime


# ──────────────────────────────────────
# Drug interaction schemas
# ──────────────────────────────────────

class DrugInteractionResponse(BaseModel):
    drug_a: str
    drug_b: str
    level: str        # "minor" | "moderate" | "major"
    category: str     # single-letter code: A, B, D, H, L, P, R, V


class InteractionAskRequest(BaseModel):
    prompt: str


class InteractionAskResponse(BaseModel):
    answer: str


# ──────────────────────────────────────
# Generic
# ──────────────────────────────────────

class MessageResponse(BaseModel):
    message: str
