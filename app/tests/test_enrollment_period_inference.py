import pytest
from datetime import datetime
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy import event
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.core.db import get_session
from app.modules.enrollment.infrastructure.models import (
    Grado,
    Acudiente,
    Estudiante,
    Periodo,
    ParametrizarMatricula,
    Matricula,
)
from sqlalchemy.pool import StaticPool

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(test_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine, expire_on_commit=False) as session:
        yield session
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture(name="client")
def client_fixture(session):
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_enrollment_period_inference_success(session, client):
    # 1. Create base data
    grado = Grado(nombre="Décimo")
    acudiente = Acudiente(
        nombre="Carlos Gomez",
        parentesco="Padre",
        telefono="3112223344",
        correo="carlos@gmail.com",
    )
    session.add(grado)
    session.add(acudiente)
    session.commit()
    session.refresh(grado)
    session.refresh(acudiente)

    estudiante = Estudiante(
        grado_id=grado.id,
        acudiente_id=acudiente.id,
        nombre="Felipe Gomez",
        documento="10987654321",
        activo=True,
        fecha_activo=datetime.now(),
    )
    session.add(estudiante)

    # Create active period for 2026
    periodo = Periodo(
        periodo_electivo=datetime(2026, 5, 20), estado=True, fecha=datetime.now()
    )
    session.add(periodo)

    # Create parametrization for 2026
    param = ParametrizarMatricula(grado_id=grado.id, anio=2026, valor=1500000)
    session.add(param)

    session.commit()
    session.refresh(estudiante)
    session.refresh(periodo)

    # 2. Test POST /register without periodo_id
    register_payload = {
        "estudiante_id": estudiante.id,
        "anio": 2026,
    }
    response = client.post("/api/v1/enrollment/register", json=register_payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["matricula_id"] is not None

    # Check that it correctly linked to the inferred period
    matricula = session.get(Matricula, response.json()["matricula_id"])
    assert matricula.periodo_id == periodo.id


def test_enrollment_period_inference_no_active_period(session, client):
    # 1. Create base data
    grado = Grado(nombre="Décimo")
    acudiente = Acudiente(
        nombre="Carlos Gomez",
        parentesco="Padre",
        telefono="3112223344",
        correo="carlos@gmail.com",
    )
    session.add(grado)
    session.add(acudiente)
    session.commit()
    session.refresh(grado)
    session.refresh(acudiente)

    estudiante = Estudiante(
        grado_id=grado.id,
        acudiente_id=acudiente.id,
        nombre="Felipe Gomez",
        documento="10987654321",
        activo=True,
        fecha_activo=datetime.now(),
    )
    session.add(estudiante)

    # No active period for 2027 (only an inactive one or one for another year)
    periodo_inactive = Periodo(
        periodo_electivo=datetime(2027, 5, 20), estado=False, fecha=datetime.now()
    )
    session.add(periodo_inactive)

    # Create parametrization for 2027
    param = ParametrizarMatricula(grado_id=grado.id, anio=2027, valor=1500000)
    session.add(param)

    session.commit()
    session.refresh(estudiante)

    # 2. Test POST /register without periodo_id for 2027 (should fail)
    register_payload = {
        "estudiante_id": estudiante.id,
        "anio": 2027,
    }
    response = client.post("/api/v1/enrollment/register", json=register_payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "No se encontró un período académico activo" in response.json()["detail"]


def test_manual_enrollment_period_inference_success(session, client):
    # 1. Create base data
    grado = Grado(nombre="Décimo")
    session.add(grado)
    session.commit()
    session.refresh(grado)

    # Create active period for 2026
    periodo = Periodo(
        periodo_electivo=datetime(2026, 1, 1), estado=True, fecha=datetime.now()
    )
    session.add(periodo)

    # Create parametrization for 2026
    param = ParametrizarMatricula(grado_id=grado.id, anio=2026, valor=1500000)
    session.add(param)

    session.commit()
    session.refresh(periodo)

    # 2. Test manual enrollment without periodo_id
    payload = {
        "documento": "12345678",
        "nombre": "Pedro Perez",
        "grado": "Décimo",
        "nombre_acudiente": "Juan Perez",
        "anio": 2026,
    }
    response = client.post("/api/v1/enrollment/students/manual", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["matricula_id"] is not None

    # Check that it correctly linked to the inferred period
    matricula = session.get(Matricula, response.json()["matricula_id"])
    assert matricula.periodo_id == periodo.id
