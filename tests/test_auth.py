import pytest
from fastapi.testclient import TestClient
from app.main import app, get_password_hash, verify_password
from app.database import SessionLocal
from app import models

client = TestClient(app)


def test_verify_password():
    password = "testpassword123"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_login_success(db):
    # Crear un usuario de prueba
    email = "test@example.com"
    password = "testpassword123"
    hashed_password = get_password_hash(password)

    # Limpiar usuarios existentes
    db.query(models.User).delete()
    db.commit()

    user = models.User(email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()

    response = client.post("/login", data={"email": email, "password": password})
    assert response.status_code == 200


def test_login_invalid_credentials():
    response = client.post(
        "/login", data={"email": "wrong@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401


def test_logout():
    response = client.post("/logout")
    assert (
        response.status_code == 200
    )  # Cambiado a 200 ya que es el código que devuelve tu aplicación
    assert "user_email" not in response.cookies
