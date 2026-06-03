import pytest
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy import event
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.core.db import get_session
from app.modules.auth.infrastructure.models import Usuario
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


def test_login_success(session, client):
    # Seed a user
    user = Usuario(
        rol="Matrícula", username="user1", contrasenia="pass123", estado=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    payload = {"username": "user1", "contrasenia": "pass123"}
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == status.HTTP_200_OK

    json_data = response.json()
    assert json_data["mensaje"] == "Inicio de sesión exitoso"
    assert json_data["usuario"]["username"] == "user1"
    assert json_data["usuario"]["rol"] == "Tesorería"
    assert json_data["usuario"]["estado"] is True
    assert "token" in json_data
    assert json_data["token"].startswith("session_token_")


def test_login_invalid_credentials(session, client):
    # Seed a user
    user = Usuario(
        rol="Administrador", username="user2", contrasenia="correct_pass", estado=True
    )
    session.add(user)
    session.commit()

    # Wrong password
    payload = {"username": "user2", "contrasenia": "wrong_pass"}
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "incorrectos" in response.json()["detail"]

    # Nonexistent username
    payload_nonexistent = {"username": "nonexistent", "contrasenia": "correct_pass"}
    response = client.post("/api/v1/auth/login", json=payload_nonexistent)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "incorrectos" in response.json()["detail"]


def test_login_inactive_user(session, client):
    # Seed inactive user
    user = Usuario(rol="Banda", username="user3", contrasenia="pass3", estado=False)
    session.add(user)
    session.commit()

    payload = {"username": "user3", "contrasenia": "pass3"}
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "inactivo" in response.json()["detail"]
