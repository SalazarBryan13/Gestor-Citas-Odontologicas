import os
import sys
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.models import User, Doctor, Patient
from app.auth import get_password_hash

# Add project root to Python path
project_root = str(Path(__file__).parent)
sys.path.insert(0, project_root)


@pytest.fixture(scope="session")
def db():
    """Create a test database session."""
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db):
    """Create a test user."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_doctor(db, test_user):
    """Create a test doctor."""
    doctor = Doctor(
        user_id=test_user.id,
        name="Test Doctor",
        specialization="General",
        license_number="12345",
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


@pytest.fixture
def test_patient(db):
    """Create a test patient."""
    patient = Patient(
        name="Test Patient", email="patient@example.com", phone="1234567890"
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient
