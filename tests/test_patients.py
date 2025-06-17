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
def test_patient(db):
    # Limpiar pacientes existentes
    db.query(models.Patient).delete()
    db.commit()

    patient = models.Patient(
        name="Patient Test", email="patient@test.com", phone="123456789"
    )
    db.add(patient)
    db.commit()
    return patient


def test_create_patient():
    patient_data = {
        "name": "New Patient",
        "email": "new@test.com",
        "phone": "987654321",
    }
    response = client.post("/patients/", json=patient_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == patient_data["name"]
    assert data["email"] == patient_data["email"]


def test_read_patients(test_patient):
    response = client.get("/patients/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(p["email"] == test_patient.email for p in data)


def test_read_patient(test_patient):
    response = client.get(f"/patients/{test_patient.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_patient.name
    assert data["email"] == test_patient.email


def test_update_patient(test_patient):
    update_data = {
        "name": "Updated Patient",
        "email": test_patient.email,
        "phone": "555555555",
    }
    response = client.put(f"/patients/{test_patient.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["phone"] == update_data["phone"]


def test_delete_patient(test_patient, db):
    # Limpiar cualquier cita asociada al paciente
    db.query(models.Appointment).filter(
        models.Appointment.patient_id == test_patient.id
    ).delete()
    db.commit()

    response = client.delete(f"/patients/{test_patient.id}")
    assert response.status_code in [
        200,
        204,
    ]  # Accept both 200 and 204 as success codes

    # Verificar que el paciente fue eliminado
    response = client.get(f"/patients/{test_patient.id}")
    assert response.status_code == 404
