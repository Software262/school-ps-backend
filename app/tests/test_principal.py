"""
Rectoría Module Integration and Unit Tests.

This module contains comprehensive integration and unit tests for the Rectoría (Principal)
FastAPI endpoints and business validations, using an in-memory SQLite database.

Author: Yessyth Jaimes
Role: Product Owner and developer of the rectoria module
"""

import pytest
from datetime import datetime
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy import event
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.core.db import get_session
from app.modules.enrollment.infrastructure.models import Docente, Periodo
from app.modules.auth.infrastructure.models import Usuario
from app.modules.principal.infrastructure.models import (
    RectoriaEstado,
    RectoriaObservaciones,
    Auditoria,
)

from sqlalchemy.pool import StaticPool

# SQLite test engine using in-memory database with StaticPool to keep connection active and shared
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(test_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Event listener to enable foreign key constraints enforcement on SQLite connections.
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture(name="session")
def session_fixture():
    """
    Fixture to create all database tables before a test and drop them after,
    running each test inside a clean database transaction context.

    Yields:
        Session: SQLModel Session with expire_on_commit=False.
    """
    # Create all tables in the test database
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine, expire_on_commit=False) as session:
        yield session
    # Drop all tables after the test
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture(name="client")
def client_fixture(session):
    """
    Fixture to override FastAPI's database session dependency with the test session,
    providing a pre-configured TestClient instance.

    Args:
        session: The test database session.

    Yields:
        TestClient: Configured TestClient for the FastAPI app.
    """

    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_get_teachers_empty(client):
    """
    Test retrieving teachers when the database is empty.

    Verifies that the endpoint returns a 200 OK status code and an empty data list.
    """
    response = client.get("/api/v1/principal/teachers")
    assert response.status_code == status.HTTP_200_OK
    json_data = response.json()
    assert json_data["statusCode"] == 200
    assert json_data["message"] == "Teachers obtained successfully"
    assert json_data["data"] == []


def test_get_teachers_with_data(session, client):
    """
    Test retrieving teachers with nested administrative statuses and observations.

    Seeds a teacher, a period, an observation, and an administrative status record,
    then asserts that the GET endpoint correctly returns them consolidated.
    """
    # Seed data
    docente = Docente(
        nombre="Juan Pérez", documento="123456", estado=True, asignatura="Matemáticas"
    )
    periodo = Periodo(
        periodo_electivo=datetime.now(), estado=True, fecha=datetime.now()
    )
    session.add(docente)
    session.add(periodo)
    session.commit()
    session.refresh(docente)
    session.refresh(periodo)

    # Seed observations and administrative status
    obs = RectoriaObservaciones(
        docente_id=docente.id,
        periodo_id=periodo.id,
        descripcion="Buen desempeño",
        tipo_observacion="Positiva",
        fecha=datetime.now(),
    )
    est = RectoriaEstado(
        docente_id=docente.id,
        periodo_id=periodo.id,
        motivo_estado="Paz y salvo administrativo",
    )
    session.add(obs)
    session.add(est)
    session.commit()

    response = client.get("/api/v1/principal/teachers")
    assert response.status_code == status.HTTP_200_OK
    json_data = response.json()
    data = json_data["data"]
    assert len(data) == 1
    assert data[0]["nombre"] == "Juan Pérez"
    assert len(data[0]["estados_administrativos"]) == 1
    assert (
        data[0]["estados_administrativos"][0]["motivo_estado"]
        == "Paz y salvo administrativo"
    )
    assert len(data[0]["observaciones"]) == 1
    assert data[0]["observaciones"][0]["descripcion"] == "Buen desempeño"


def test_create_observation_success(session, client):
    """
    Test successful creation of a teacher administrative observation.

    Seeds a teacher, an academic period, and an authorized user in the database.
    Sends a POST request to register a new observation and asserts:
    - HTTP status code is 200 OK.
    - JSON payload status code is 200.
    - Observation description matches the payload.
    - A corresponding log is added to the system audit trail.
    """
    # Seed relations
    docente = Docente(
        nombre="Juan Pérez", documento="123456", estado=True, asignatura="Matemáticas"
    )
    periodo = Periodo(
        periodo_electivo=datetime.now(), estado=True, fecha=datetime.now()
    )
    usuario = Usuario(rol="Rectoría", username="rector", contrasenia="123", estado=True)
    session.add(docente)
    session.add(periodo)
    session.add(usuario)
    session.commit()
    session.refresh(docente)
    session.refresh(periodo)
    session.refresh(usuario)

    payload = {
        "docente_id": docente.id,
        "periodo_id": periodo.id,
        "id_usuario": usuario.id,
        "descripcion": "Observación sobre el docente",
        "tipo_observacion": "General",
    }

    response = client.post("/api/v1/principal/observations", json=payload)
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
    json_data = response.json()
    assert json_data["statusCode"] == 200
    assert json_data["message"] == "Administrative observation created successfully"
    assert json_data["data"]["descripcion"] == "Observación sobre el docente"

    # Verify audit log
    audit = (
        session.query(Auditoria)
        .filter(Auditoria.tabla_nombre == "RectoriaObservaciones")
        .first()
    )
    assert audit is not None
    assert audit.id_usuario == usuario.id
    assert audit.operacion == "INSERT"
    assert "descripcion=" in audit.valor_nuevo


def test_create_observation_invalid_relations(session, client):
    """
    Test observation creation fails when foreign relations are invalid.

    Verifies that requests containing non-existent docente, period, or user identifiers
    are rejected with a 400 Bad Request status code.
    """
    # Seed partial relations
    docente = Docente(
        nombre="Juan Pérez", documento="123456", estado=True, asignatura="Matemáticas"
    )
    periodo = Periodo(
        periodo_electivo=datetime.now(), estado=True, fecha=datetime.now()
    )
    usuario = Usuario(rol="Rectoría", username="rector", contrasenia="123", estado=True)
    session.add(docente)
    session.add(periodo)
    session.add(usuario)
    session.commit()
    session.refresh(docente)
    session.refresh(periodo)
    session.refresh(usuario)

    # Invalid Usuario
    payload = {
        "docente_id": docente.id,
        "periodo_id": periodo.id,
        "id_usuario": 999,
        "descripcion": "Observación sobre el docente",
        "tipo_observacion": "General",
    }
    response = client.post("/api/v1/principal/observations", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "El usuario no existe" in response.json()["detail"]

    # Invalid Docente
    payload = {
        "docente_id": 999,
        "periodo_id": periodo.id,
        "id_usuario": usuario.id,
        "descripcion": "Observación sobre el docente",
        "tipo_observacion": "General",
    }
    response = client.post("/api/v1/principal/observations", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "El docente no existe" in response.json()["detail"]

    # Invalid Periodo
    payload = {
        "docente_id": docente.id,
        "periodo_id": 999,
        "id_usuario": usuario.id,
        "descripcion": "Observación sobre el docente",
        "tipo_observacion": "General",
    }
    response = client.post("/api/v1/principal/observations", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "El periodo no existe" in response.json()["detail"]


def test_create_observation_unauthorized_role(session, client):
    """
    Test observation creation is rejected for users without Rectoría/Admin roles.

    Verifies that a user with an unauthorized role (e.g. Docente) fails validation
    and returns a 400 Bad Request status code.
    """
    docente = Docente(
        nombre="Juan Pérez", documento="123456", estado=True, asignatura="Matemáticas"
    )
    periodo = Periodo(
        periodo_electivo=datetime.now(), estado=True, fecha=datetime.now()
    )
    usuario = Usuario(
        rol="Docente", username="docente1", contrasenia="123", estado=True
    )
    session.add(docente)
    session.add(periodo)
    session.add(usuario)
    session.commit()
    session.refresh(docente)
    session.refresh(periodo)
    session.refresh(usuario)

    payload = {
        "docente_id": docente.id,
        "periodo_id": periodo.id,
        "id_usuario": usuario.id,
        "descripcion": "Observación sobre el docente",
        "tipo_observacion": "General",
    }
    response = client.post("/api/v1/principal/observations", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        "El usuario no tiene permisos de Rectoría o Administrador"
        in response.json()["detail"]
    )


def test_create_status_success(session, client):
    """
    Test successful administrative status assignment and duplicate prevention.

    Seeds required relations and posts a new status payload. Verifies 201 JSON status code
    and asserts that a duplicate status request is rejected with a 400 Bad Request.
    """
    docente = Docente(
        nombre="Juan Pérez", documento="123456", estado=True, asignatura="Matemáticas"
    )
    periodo = Periodo(
        periodo_electivo=datetime.now(), estado=True, fecha=datetime.now()
    )
    usuario = Usuario(
        rol="Administrador", username="admin", contrasenia="123", estado=True
    )
    session.add(docente)
    session.add(periodo)
    session.add(usuario)
    session.commit()
    session.refresh(docente)
    session.refresh(periodo)
    session.refresh(usuario)

    payload = {
        "docente_id": docente.id,
        "periodo_id": periodo.id,
        "id_usuario": usuario.id,
        "motivo_estado": "Pendiente de paz y salvo",
    }
    response = client.post("/api/v1/principal/status", json=payload)
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
    json_data = response.json()
    assert json_data["statusCode"] == 200
    assert json_data["message"] == "Administrative status created successfully"
    assert json_data["data"]["motivo_estado"] == "Pendiente de paz y salvo"

    # Verify duplicate creation error
    response_dup = client.post("/api/v1/principal/status", json=payload)
    assert response_dup.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        "Ya existe un estado administrativo para ese docente y periodo"
        in response_dup.json()["detail"]
    )


def test_create_status_invalid_relations(session, client):
    """
    Test status assignment fails when foreign relations are invalid.

    Verifies that requests containing non-existent docente, period, or user identifiers
    are rejected with a 400 Bad Request status code.
    """
    docente = Docente(
        nombre="Juan Pérez", documento="123456", estado=True, asignatura="Matemáticas"
    )
    periodo = Periodo(
        periodo_electivo=datetime.now(), estado=True, fecha=datetime.now()
    )
    usuario = Usuario(
        rol="Administrador del Sistema",
        username="admin",
        contrasenia="123",
        estado=True,
    )
    session.add(docente)
    session.add(periodo)
    session.add(usuario)
    session.commit()
    session.refresh(docente)
    session.refresh(periodo)
    session.refresh(usuario)

    # Invalid user
    payload = {
        "docente_id": docente.id,
        "periodo_id": periodo.id,
        "id_usuario": 999,
        "motivo_estado": "Pendiente",
    }
    response = client.post("/api/v1/principal/status", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "El usuario no existe" in response.json()["detail"]

    # Invalid docente
    payload = {
        "docente_id": 999,
        "periodo_id": periodo.id,
        "id_usuario": usuario.id,
        "motivo_estado": "Pendiente",
    }
    response = client.post("/api/v1/principal/status", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "El docente no existe" in response.json()["detail"]

    # Invalid periodo
    payload = {
        "docente_id": docente.id,
        "periodo_id": 999,
        "id_usuario": usuario.id,
        "motivo_estado": "Pendiente",
    }
    response = client.post("/api/v1/principal/status", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "El periodo no existe" in response.json()["detail"]


def test_update_status_success(session, client):
    """
    Test successful update of an existing administrative status record.

    Modifies an existing record's motivo_estado, asserts 200 OK status code,
    and verifies that the audit log registers a correct UPDATE transition.
    """
    docente = Docente(
        nombre="Juan Pérez", documento="123456", estado=True, asignatura="Matemáticas"
    )
    periodo = Periodo(
        periodo_electivo=datetime.now(), estado=True, fecha=datetime.now()
    )
    usuario = Usuario(rol="Rectoría", username="rector", contrasenia="123", estado=True)
    session.add(docente)
    session.add(periodo)
    session.add(usuario)
    session.commit()
    session.refresh(docente)
    session.refresh(periodo)
    session.refresh(usuario)

    status_obj = RectoriaEstado(
        docente_id=docente.id, periodo_id=periodo.id, motivo_estado="Pendiente"
    )
    session.add(status_obj)
    session.commit()
    session.refresh(status_obj)

    payload = {"id_usuario": usuario.id, "motivo_estado": "Paz y salvo total"}
    response = client.put(f"/api/v1/principal/status/{status_obj.id}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    json_data = response.json()
    assert json_data["message"] == "Administrative status updated successfully"
    assert json_data["statusCode"] == 200
    assert json_data["data"]["motivo_estado"] == "Paz y salvo total"

    # Verify audit log
    audit = (
        session.query(Auditoria)
        .filter(
            Auditoria.tabla_nombre == "RectoriaEstado", Auditoria.operacion == "UPDATE"
        )
        .first()
    )
    assert audit is not None
    assert audit.valor_anterior == "Pendiente"
    assert audit.valor_nuevo == "Paz y salvo total"


def test_update_status_not_found(session, client):
    """
    Test status update fails when the status record ID does not exist.

    Verifies that a PUT request for a non-existent status ID is rejected with 404 Not Found.
    """
    usuario = Usuario(rol="Rectoría", username="rector", contrasenia="123", estado=True)
    session.add(usuario)
    session.commit()
    session.refresh(usuario)

    payload = {"id_usuario": usuario.id, "motivo_estado": "Paz y salvo"}
    response = client.put("/api/v1/principal/status/999", json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Administrative status not found" in response.json()["detail"]


def test_update_status_invalid_user(session, client):
    """
    Test status update fails when the executing user ID is invalid.

    Verifies that a PUT request containing a non-existent user identifier is rejected with 400 Bad Request.
    """
    docente = Docente(
        nombre="Juan Pérez", documento="123456", estado=True, asignatura="Matemáticas"
    )
    periodo = Periodo(
        periodo_electivo=datetime.now(), estado=True, fecha=datetime.now()
    )
    session.add(docente)
    session.add(periodo)
    session.commit()
    session.refresh(docente)
    session.refresh(periodo)

    status_obj = RectoriaEstado(
        docente_id=docente.id, periodo_id=periodo.id, motivo_estado="Pendiente"
    )
    session.add(status_obj)
    session.commit()
    session.refresh(status_obj)

    payload = {"id_usuario": 999, "motivo_estado": "Paz y salvo"}
    response = client.put(f"/api/v1/principal/status/{status_obj.id}", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "El usuario no existe" in response.json()["detail"]


def test_update_status_unauthorized_role(session, client):
    """
    Test status update fails when executing user role is not authorized.

    Verifies that a PUT request containing a user without Rectoría or Admin role is rejected with 400 Bad Request.
    """
    docente = Docente(
        nombre="Juan Pérez", documento="123456", estado=True, asignatura="Matemáticas"
    )
    periodo = Periodo(
        periodo_electivo=datetime.now(), estado=True, fecha=datetime.now()
    )
    usuario = Usuario(
        rol="Docente", username="docente1", contrasenia="123", estado=True
    )
    session.add(docente)
    session.add(periodo)
    session.add(usuario)
    session.commit()
    session.refresh(docente)
    session.refresh(periodo)
    session.refresh(usuario)

    status_obj = RectoriaEstado(
        docente_id=docente.id, periodo_id=periodo.id, motivo_estado="Pendiente"
    )
    session.add(status_obj)
    session.commit()
    session.refresh(status_obj)

    payload = {"id_usuario": usuario.id, "motivo_estado": "Paz y salvo"}
    response = client.put(f"/api/v1/principal/status/{status_obj.id}", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        "El usuario no tiene permisos de Rectoría o Administrador"
        in response.json()["detail"]
    )
