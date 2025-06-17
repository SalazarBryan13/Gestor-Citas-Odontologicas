from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import sqlite3
import os

from . import models, schemas, database
from .database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gestor de Citas Médicas")

# Configuración de seguridad
SECRET_KEY = "tu_clave_secreta_aqui"  # En producción, usar una clave segura
ALGORITHM = "HS256"

# Configuración de autenticación
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Modelos
class User(BaseModel):
    email: str
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str


# Funciones de autenticación
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(email: str):
    conn = sqlite3.connect("gestor_citas.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    if user:
        return UserInDB(email=user[1], hashed_password=user[2])
    return None


def authenticate_user(email: str, password: str):
    user = get_user(email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


# Función para verificar autenticación
async def verify_auth(request: Request):
    user_email = request.cookies.get("user_email")
    if not user_email:
        return False
    user = get_user(user_email)
    return bool(user)


# Rutas principales
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    if not await verify_auth(request):
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/doctors", response_class=HTMLResponse)
async def doctors_page(request: Request):
    if not await verify_auth(request):
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("doctors.html", {"request": request})


@app.get("/patients", response_class=HTMLResponse)
async def patients_page(request: Request):
    if not await verify_auth(request):
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("patients.html", {"request": request})


@app.get("/appointments", response_class=HTMLResponse)
async def appointments_page(request: Request):
    if not await verify_auth(request):
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("appointments.html", {"request": request})


@app.post("/login")
async def login(request: Request):
    form_data = await request.form()
    email = form_data.get("email")
    password = form_data.get("password")

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required",
        )

    user = authenticate_user(email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="user_email", value=user.email, httponly=True, secure=True, samesite="lax"
    )
    return response


@app.post("/users/")
async def create_user(user_data: dict):
    email = user_data.get("email")
    password = user_data.get("password")

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required",
        )

    # Verificar si el usuario ya existe
    if get_user(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Crear nuevo usuario
    hashed_password = get_password_hash(password)
    conn = sqlite3.connect("gestor_citas.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (email, hashed_password) VALUES (?, ?)",
        (email, hashed_password),
    )
    conn.commit()
    conn.close()

    return {"message": "User created successfully"}


@app.post("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("user_email")
    return response


# Rutas de la API
@app.get("/doctors/", response_model=List[schemas.Doctor])
def read_doctors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        doctors = db.query(models.Doctor).offset(skip).limit(limit).all()
        return doctors
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los doctores: {str(e)}",
        )


@app.post("/doctors/", response_model=schemas.Doctor)
def create_doctor(doctor: schemas.DoctorCreate, db: Session = Depends(get_db)):
    try:
        # Validar que el email no esté duplicado
        existing_doctor = (
            db.query(models.Doctor).filter(models.Doctor.email == doctor.email).first()
        )
        if existing_doctor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un doctor con ese email",
            )

        # Validar que el teléfono no esté duplicado
        existing_phone = (
            db.query(models.Doctor).filter(models.Doctor.phone == doctor.phone).first()
        )
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un doctor con ese número de teléfono",
            )

        # Crear el nuevo doctor
        db_doctor = models.Doctor(
            name=doctor.name,
            specialization=doctor.specialization,
            email=doctor.email,
            phone=doctor.phone,
        )
        db.add(db_doctor)
        db.commit()
        db.refresh(db_doctor)
        return db_doctor
    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el doctor: {str(e)}",
        )


@app.post("/patients/", response_model=schemas.Patient)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    try:
        # Validar que el email no esté duplicado
        existing_patient = (
            db.query(models.Patient)
            .filter(models.Patient.email == patient.email)
            .first()
        )
        if existing_patient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un paciente con ese email",
            )

        # Validar que el teléfono no esté duplicado
        existing_phone = (
            db.query(models.Patient)
            .filter(models.Patient.phone == patient.phone)
            .first()
        )
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un paciente con ese número de teléfono",
            )

        # Crear el nuevo paciente
        db_patient = models.Patient(
            name=patient.name, email=patient.email, phone=patient.phone
        )
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)
        return db_patient
    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el paciente: {str(e)}",
        )


@app.post("/appointments/", response_model=schemas.Appointment)
def create_appointment(
    appointment: schemas.AppointmentCreate, db: Session = Depends(get_db)
):
    # Check if patient already has an appointment
    existing_appointment = (
        db.query(models.Appointment)
        .filter(models.Appointment.patient_id == appointment.patient_id)
        .first()
    )
    if existing_appointment:
        # Obtener información del paciente y la cita existente
        patient = (
            db.query(models.Patient)
            .filter(models.Patient.id == appointment.patient_id)
            .first()
        )
        doctor = (
            db.query(models.Doctor)
            .filter(models.Doctor.id == existing_appointment.doctor_id)
            .first()
        )

        if not patient or not doctor:
            raise HTTPException(
                status_code=404, detail="Paciente o doctor no encontrado"
            )

        date_time = existing_appointment.date_time.strftime("%d/%m/%Y %H:%M")
        raise HTTPException(
            status_code=400,
            detail=f"El paciente {patient.name} ya tiene una cita programada con el Dr. {doctor.name} para el {date_time}",
        )

    db_appointment = models.Appointment(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment


@app.get("/patients/", response_model=List[schemas.Patient])
def read_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    patients = db.query(models.Patient).offset(skip).limit(limit).all()
    return patients


@app.get("/appointments/", response_model=List[schemas.Appointment])
def read_appointments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    appointments = db.query(models.Appointment).offset(skip).limit(limit).all()
    return appointments


@app.get("/doctors/{doctor_id}", response_model=schemas.Doctor)
def read_doctor(doctor_id: int, db: Session = Depends(get_db)):
    try:
        doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Doctor no encontrado"
            )
        return doctor
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el doctor: {str(e)}",
        )


@app.put("/doctors/{doctor_id}", response_model=schemas.Doctor)
def update_doctor(
    doctor_id: int, doctor: schemas.DoctorCreate, db: Session = Depends(get_db)
):
    try:
        db_doctor = (
            db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
        )
        if not db_doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Doctor no encontrado"
            )

        # Validar que el email no esté duplicado (si se cambió)
        if doctor.email != db_doctor.email:
            existing_doctor = (
                db.query(models.Doctor)
                .filter(
                    models.Doctor.email == doctor.email, models.Doctor.id != doctor_id
                )
                .first()
            )
            if existing_doctor:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un doctor con ese email",
                )

        # Validar que el teléfono no esté duplicado (si se cambió)
        if doctor.phone != db_doctor.phone:
            existing_phone = (
                db.query(models.Doctor)
                .filter(
                    models.Doctor.phone == doctor.phone, models.Doctor.id != doctor_id
                )
                .first()
            )
            if existing_phone:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un doctor con ese número de teléfono",
                )

        # Actualizar los datos del doctor
        db_doctor.name = doctor.name
        db_doctor.specialization = doctor.specialization
        db_doctor.email = doctor.email
        db_doctor.phone = doctor.phone

        db.commit()
        db.refresh(db_doctor)
        return db_doctor
    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el doctor: {str(e)}",
        )


@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    try:
        db_doctor = (
            db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
        )
        if not db_doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Doctor no encontrado"
            )

        # Verificar si el doctor tiene citas asociadas
        appointments = (
            db.query(models.Appointment)
            .filter(models.Appointment.doctor_id == doctor_id)
            .first()
        )
        if appointments:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar el doctor porque tiene citas asociadas",
            )

        db.delete(db_doctor)
        db.commit()
        return {"message": "Doctor eliminado exitosamente"}
    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el doctor: {str(e)}",
        )


@app.get("/patients/{patient_id}", response_model=schemas.Patient)
def read_patient(patient_id: int, db: Session = Depends(get_db)):
    try:
        patient = (
            db.query(models.Patient).filter(models.Patient.id == patient_id).first()
        )
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado"
            )
        return patient
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el paciente: {str(e)}",
        )


@app.put("/patients/{patient_id}", response_model=schemas.Patient)
def update_patient(
    patient_id: int, patient: schemas.PatientCreate, db: Session = Depends(get_db)
):
    try:
        db_patient = (
            db.query(models.Patient).filter(models.Patient.id == patient_id).first()
        )
        if not db_patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado"
            )

        # Validar que el email no esté duplicado (si se cambió)
        if patient.email != db_patient.email:
            existing_patient = (
                db.query(models.Patient)
                .filter(
                    models.Patient.email == patient.email,
                    models.Patient.id != patient_id,
                )
                .first()
            )
            if existing_patient:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un paciente con ese email",
                )

        # Validar que el teléfono no esté duplicado (si se cambió)
        if patient.phone != db_patient.phone:
            existing_phone = (
                db.query(models.Patient)
                .filter(
                    models.Patient.phone == patient.phone,
                    models.Patient.id != patient_id,
                )
                .first()
            )
            if existing_phone:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ya existe un paciente con ese número de teléfono",
                )

        # Actualizar los datos del paciente
        db_patient.name = patient.name
        db_patient.email = patient.email
        db_patient.phone = patient.phone

        db.commit()
        db.refresh(db_patient)
        return db_patient
    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el paciente: {str(e)}",
        )


@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    try:
        db_patient = (
            db.query(models.Patient).filter(models.Patient.id == patient_id).first()
        )
        if not db_patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado"
            )

        # Verificar si el paciente tiene citas asociadas
        appointments = (
            db.query(models.Appointment)
            .filter(models.Appointment.patient_id == patient_id)
            .first()
        )
        if appointments:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar el paciente porque tiene citas asociadas",
            )

        db.delete(db_patient)
        db.commit()
        return {"message": "Paciente eliminado exitosamente"}
    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el paciente: {str(e)}",
        )


@app.get("/appointments/{appointment_id}", response_model=schemas.Appointment)
def read_appointment(appointment_id: int, db: Session = Depends(get_db)):
    try:
        appointment = (
            db.query(models.Appointment)
            .filter(models.Appointment.id == appointment_id)
            .first()
        )
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Cita no encontrada"
            )
        return appointment
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la cita: {str(e)}",
        )


@app.put("/appointments/{appointment_id}", response_model=schemas.Appointment)
def update_appointment(
    appointment_id: int,
    appointment: schemas.AppointmentCreate,
    db: Session = Depends(get_db),
):
    try:
        db_appointment = (
            db.query(models.Appointment)
            .filter(models.Appointment.id == appointment_id)
            .first()
        )
        if not db_appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Cita no encontrada"
            )

        # Verificar si el doctor existe
        doctor = (
            db.query(models.Doctor)
            .filter(models.Doctor.id == appointment.doctor_id)
            .first()
        )
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El doctor seleccionado no existe",
            )

        # Verificar si el paciente existe
        patient = (
            db.query(models.Patient)
            .filter(models.Patient.id == appointment.patient_id)
            .first()
        )
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El paciente seleccionado no existe",
            )

        # Verificar si hay conflicto de horario para el doctor
        conflicting_appointment = (
            db.query(models.Appointment)
            .filter(
                models.Appointment.doctor_id == appointment.doctor_id,
                models.Appointment.date_time == appointment.date_time,
                models.Appointment.id != appointment_id,
            )
            .first()
        )
        if conflicting_appointment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El doctor ya tiene una cita programada en ese horario",
            )

        # Verificar si hay conflicto de horario para el paciente
        conflicting_patient_appointment = (
            db.query(models.Appointment)
            .filter(
                models.Appointment.patient_id == appointment.patient_id,
                models.Appointment.date_time == appointment.date_time,
                models.Appointment.id != appointment_id,
            )
            .first()
        )
        if conflicting_patient_appointment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El paciente ya tiene una cita programada en ese horario",
            )

        # Actualizar los datos de la cita
        db_appointment.date_time = appointment.date_time
        db_appointment.doctor_id = appointment.doctor_id
        db_appointment.patient_id = appointment.patient_id
        db_appointment.status = appointment.status

        db.commit()
        db.refresh(db_appointment)
        return db_appointment
    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar la cita: {str(e)}",
        )


@app.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    try:
        db_appointment = (
            db.query(models.Appointment)
            .filter(models.Appointment.id == appointment_id)
            .first()
        )
        if not db_appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Cita no encontrada"
            )

        db.delete(db_appointment)
        db.commit()
        return {"message": "Cita eliminada exitosamente"}
    except HTTPException as he:
        db.rollback()
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar la cita: {str(e)}",
        )


# Inicialización de la base de datos
def init_db():
    conn = sqlite3.connect("gestor_citas.db")
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  email TEXT UNIQUE NOT NULL,
                  hashed_password TEXT NOT NULL)"""
    )
    conn.commit()
    conn.close()


# Inicializar la base de datos al iniciar la aplicación
init_db()
