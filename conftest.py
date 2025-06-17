import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent)
sys.path.insert(0, project_root)

from app.database import Base, engine, SessionLocal
from app.models import User, Doctor, Patient, Appointment
from app.auth import get_password_hash

@pytest.fixture(scope="session")
def db():
    # Create the database and tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new database session
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Clean up the database after tests
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(db):
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_doctor(db, test_user):
    doctor = Doctor(
        name="Dr. Test",
        specialization="General",
        user_id=test_user.id
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor

@pytest.fixture
def test_patient(db):
    patient = Patient(
        name="Test Patient",
        email="patient@example.com",
        phone="1234567890"
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient 