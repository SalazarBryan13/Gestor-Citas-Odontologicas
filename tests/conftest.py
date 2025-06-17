import pytest
import os
from app.database import Base, engine, SessionLocal
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def test_db():
    # Crear una base de datos de prueba
    test_db_path = "test.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    # Crear las tablas
    Base.metadata.create_all(bind=engine)

    yield

    # Limpiar después de las pruebas
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.fixture(scope="function")
def db(test_db):
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(test_db):
    with TestClient(app) as test_client:
        yield test_client
