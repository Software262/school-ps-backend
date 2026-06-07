import pytest
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy import event
from sqlalchemy.pool import StaticPool
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.core.db import get_session
from app.modules.enrollment.infrastructure.models import Complementario

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


def test_get_complementary_concepts_endpoint(session, client):
    c1 = Complementario(
        tipo_complementario="Seguro Estudiantil",
        anio=2026,
        valor=50000,
        estado_complemento="Activo",
        uso_matricula=True,
    )
    c2 = Complementario(
        tipo_complementario="Sistematización",
        anio=2026,
        valor=30000,
        estado_complemento="Activo",
        uso_matricula=False,
    )
    c3 = Complementario(
        tipo_complementario="Pensión Especial",
        anio=2026,
        valor=100000,
        estado_complemento="Inactivo",
        uso_matricula=True,
    )
    c4 = Complementario(
        tipo_complementario="Derechos de Grado",
        anio=2025,
        valor=80000,
        estado_complemento="Activo",
        uso_matricula=True,
    )
    session.add_all([c1, c2, c3, c4])
    session.commit()

    resp = client.get("/api/v1/enrollment/complementary", params={"year": 2026})
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()

    assert len(data) == 2
    assert {c["tipo_complementario"] for c in data} == {
        "Seguro Estudiantil",
        "Sistematización",
    }
    assert {c["valor"] for c in data} == {50000, 30000}
