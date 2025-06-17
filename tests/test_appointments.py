import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app import models
from datetime import datetime, timedelta

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
    db.refresh(patient)
    return patient


@pytest.fixture
def test_appointment(db, test_doctor, test_patient):
    # Limpiar citas existentes
    db.query(models.Appointment).delete()
    db.commit()

    appointment = models.Appointment(
        doctor_id=test_doctor.id,
        patient_id=test_patient.id,
        date_time=datetime.now() + timedelta(days=1),
        status="scheduled",
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


def test_create_appointment(test_doctor, test_patient, db):
    # Limpiar citas existentes
    db.query(models.Appointment).delete()
    db.commit()

    appointment_data = {
        "doctor_id": test_doctor.id,
        "patient_id": test_patient.id,
        "date_time": (datetime.now() + timedelta(days=2)).isoformat(),
        "status": "scheduled",
    }
    response = client.post("/appointments/", json=appointment_data)
    assert response.status_code == 200
    data = response.json()
    assert data["doctor_id"] == test_doctor.id
    assert data["patient_id"] == test_patient.id


def test_read_appointments(test_appointment):
    response = client.get("/appointments/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(a["id"] == test_appointment.id for a in data)


def test_read_appointment(test_appointment):
    response = client.get(f"/appointments/{test_appointment.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["doctor_id"] == test_appointment.doctor_id
    assert data["patient_id"] == test_appointment.patient_id


def test_update_appointment(test_appointment):
    update_data = {
        "doctor_id": test_appointment.doctor_id,
        "patient_id": test_appointment.patient_id,
        "date_time": (datetime.now() + timedelta(days=3)).isoformat(),
        "status": "completed",
    }
    response = client.put(f"/appointments/{test_appointment.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"


def test_delete_appointment(test_appointment):
    response = client.delete(f"/appointments/{test_appointment.id}")
    assert response.status_code == 200

    # Verificar que la cita fue eliminada
    response = client.get(f"/appointments/{test_appointment.id}")
    assert response.status_code == 404


def test_duplicate_appointment(test_doctor, test_patient):
    # Crear primera cita
    appointment_data = {
        "doctor_id": test_doctor.id,
        "patient_id": test_patient.id,
        "date_time": (datetime.now() + timedelta(days=1)).isoformat(),
        "status": "scheduled",
    }
    response = client.post("/appointments/", json=appointment_data)
    assert response.status_code == 200

    # Intentar crear una cita duplicada
    response = client.post("/appointments/", json=appointment_data)
    assert response.status_code == 400
    assert "ya tiene una cita programada" in response.json()["detail"]
