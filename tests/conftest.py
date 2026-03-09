import pytest
import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Base, get_db
from models.db_models import User
from auth import hash_password, create_access_token
from main import app

# Create an in-memory SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    # Setup test DB tables
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    # Teardown test DB tables
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def db_session():
    # Setup for DB interactions within tests (like seeding)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function", autouse=True)
def clean_db():
    # Clean up the tables before/after each test function to guarantee isolation
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_header(db_session):
    # Create test user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("password123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Generate token
    token = create_access_token(data={"sub": user.username})
    return {"Authorization": f"Bearer {token}"}
