from datetime import datetime
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.core.db import get_session
from app.main import app
from app.modules.enrollment.infrastructure.models import (
    Acudiente,
    Complementario,
    Estudiante,
    Grado,
    ParametrizarMatricula,
    Periodo,
    TipoComplementario,
)
from app.modules.tuition.infrastructure.models import ParametrizarPension, Pension

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


def test_enrollment_creates_pension_success(session, client):
    # 1. Seed base data
    grado = Grado(nombre="Sexto")
    session.add(grado)
    session.commit()
    session.refresh(grado)

    periodo = Periodo(
        periodo_electivo=datetime(2026, 1, 1), estado=True, fecha=datetime.now()
    )
    session.add(periodo)
    session.commit()
    session.refresh(periodo)

    acudiente = Acudiente(
        nombre="Carlos Gomez",
        parentesco="Padre",
        telefono="3112223344",
        correo="carlos@gmail.com",
    )
    session.add(acudiente)
    session.commit()
    session.refresh(acudiente)

    student = Estudiante(
        nombre="Juan Andres",
        documento="1005777888",
        grado_id=grado.id,
        acudiente_id=acudiente.id,
        activo=True,
    )
    session.add(student)
    session.commit()
    session.refresh(student)

    param_mat = ParametrizarMatricula(grado_id=grado.id or 1, anio=2026, valor=850000)
    session.add(param_mat)

    param_pen = ParametrizarPension(grado_id=grado.id or 1, anio=2026, valor=1500000)
    session.add(param_pen)
    session.commit()

    # 2. Register automatic enrollment
    payload = {
        "estudiante_id": student.id,
        "periodo_id": periodo.id,
        "anio": 2026,
    }
    response = client.post("/api/v1/enrollment/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    # 3. Verify that the Pension record was auto-created
    pension_records = session.exec(
        select(Pension).where(Pension.estudiante_id == student.id)
    ).all()
    assert len(pension_records) == 1
    pension = pension_records[0]
    assert pension.grado_id == grado.id
    assert pension.para_pension_id == param_pen.id
    assert pension.valor_total == 1500000
    assert pension.estado_pension is False


def test_enrollment_creates_pension_default_parametrization(session, client):
    # 1. Seed base data without seeding ParametrizarPension
    grado = Grado(nombre="Sexto")
    session.add(grado)
    session.commit()
    session.refresh(grado)

    periodo = Periodo(
        periodo_electivo=datetime(2026, 1, 1), estado=True, fecha=datetime.now()
    )
    session.add(periodo)
    session.commit()
    session.refresh(periodo)

    acudiente = Acudiente(
        nombre="Carlos Gomez",
        parentesco="Padre",
        telefono="3112223344",
        correo="carlos@gmail.com",
    )
    session.add(acudiente)
    session.commit()
    session.refresh(acudiente)

    student = Estudiante(
        nombre="Juan Andres",
        documento="1005777888",
        grado_id=grado.id,
        acudiente_id=acudiente.id,
        activo=True,
    )
    session.add(student)
    session.commit()
    session.refresh(student)

    param_mat = ParametrizarMatricula(grado_id=grado.id or 1, anio=2026, valor=850000)
    session.add(param_mat)
    session.commit()

    # 2. Register automatic enrollment
    payload = {
        "estudiante_id": student.id,
        "periodo_id": periodo.id,
        "anio": 2026,
    }
    response = client.post("/api/v1/enrollment/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED

    # 3. Verify ParametrizarPension was auto-seeded with valor=0
    param_pens = session.exec(
        select(ParametrizarPension).where(
            ParametrizarPension.grado_id == grado.id, ParametrizarPension.anio == 2026
        )
    ).all()
    assert len(param_pens) == 1
    assert param_pens[0].valor == 0

    # 4. Verify Pension record was auto-created with valor_total=0
    pension_records = session.exec(
        select(Pension).where(Pension.estudiante_id == student.id)
    ).all()
    assert len(pension_records) == 1
    pension = pension_records[0]
    assert pension.grado_id == grado.id
    assert pension.para_pension_id == param_pens[0].id
    assert pension.valor_total == 0


def test_create_complementary_default_type(session, client):
    # 1. Post request without specifying tipo_complementario_id
    payload = {
        "nombre": "Seguro Contra Accidentes",
        "anio": 2026,
        "valor": 75000,
        "estado_complemento": "Activo",
    }
    response = client.post("/api/v1/enrollment/complementary", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "complementario_id" in data

    # 2. Verify in DB that it is linked to "Matricula" type
    comp_id = data["complementario_id"]
    comp = session.get(Complementario, comp_id)
    assert comp is not None
    assert comp.nombre == "Seguro Contra Accidentes"

    tipo = session.get(TipoComplementario, comp.tipo_complementario_id)
    assert tipo is not None
    assert tipo.nombre.lower() == "matricula"
