from fastapi import APIRouter, HTTPException, status
from models.schemas import UserCreate, UserLogin, TokenResponse, MessageResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate):
    """Register a new user account."""
    # TODO: hash password, store user in database
    return MessageResponse(message=f"User '{user.username}' registered successfully.")


@router.post("/login", response_model=TokenResponse)
async def login(user: UserLogin):
    """Authenticate a user and return a JWT access token."""
    # TODO: verify credentials against database, generate real JWT
    return TokenResponse(access_token="stub-jwt-token")
