import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app import models

client = TestClient(app)


@pytest.fixture
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_doctor(db):
    # Limpiar doctores existentes
    db.query(models.Doctor).delete()
    db.commit()

    doctor = models.Doctor(
        name="Dr. Test",
        email="doctor@test.com",
        phone="123456789",
        specialization="General",
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


def test_create_doctor():
    doctor_data = {
        "name": "Dr. New",
        "email": "new@test.com",
        "phone": "987654321",
        "specialization": "Cardiology",
    }
    response = client.post("/doctors/", json=doctor_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == doctor_data["name"]
    assert data["email"] == doctor_data["email"]


def test_read_doctors(test_doctor):
    response = client.get("/doctors/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(d["email"] == test_doctor.email for d in data)


def test_read_doctor(test_doctor):
    response = client.get(f"/doctors/{test_doctor.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_doctor.name
    assert data["email"] == test_doctor.email


def test_update_doctor(test_doctor):
    update_data = {
        "name": "Dr. Updated",
        "email": test_doctor.email,
        "phone": "555555555",
        "specialization": "Updated Specialization",
    }
    response = client.put(f"/doctors/{test_doctor.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["phone"] == update_data["phone"]


def test_delete_doctor(test_doctor, db):
    # Primero verificar que el doctor existe
    response = client.get(f"/doctors/{test_doctor.id}")
    assert response.status_code == 200

    # Limpiar cualquier cita asociada al doctor
    db.query(models.Appointment).filter(
        models.Appointment.doctor_id == test_doctor.id
    ).delete()
    db.commit()

    # Luego intentar eliminarlo
    response = client.delete(f"/doctors/{test_doctor.id}")
    assert response.status_code in [
        200,
        204,
    ]  # Accept both 200 and 204 as success codes

    # Verificar que ya no existe
    response = client.get(f"/doctors/{test_doctor.id}")
    assert response.status_code == 404
