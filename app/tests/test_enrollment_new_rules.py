from datetime import datetime
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

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


def test_modified_enrollment_base_cost_in_balance(session, client):
    # 1. Seed base data
    grado = Grado(nombre="Décimo")
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
        nombre="Juan Perez Sr",
        parentesco="Padre",
        telefono="3112223344",
        correo="carlos@gmail.com",
    )
    session.add(acudiente)
    session.commit()
    session.refresh(acudiente)

    student = Estudiante(
        nombre="Juan Perez Jr",
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

    # 2. Register enrollment
    payload = {
        "estudiante_id": student.id,
        "periodo_id": periodo.id,
        "anio": 2026,
    }
    response = client.post("/api/v1/enrollment/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    matricula_id = data["matricula_id"]

    # 3. Check initial balance
    balance_resp = client.get(
        f"/api/v1/enrollment/students/{student.id}/balance?year=2026"
    )
    assert balance_resp.status_code == 200
    balance_data = balance_resp.json()
    assert balance_data["costo_base_matricula"] == 850000
    assert balance_data["total_pendiente"] == 850000

    # 4. Modify enrollment applying a discount on base tuition
    modify_payload = {
        "motivo": "Buen rendimiento",
        "descuento_base": 150000,
    }
    modify_resp = client.put(
        f"/api/v1/enrollment/students/{matricula_id}/matricula", json=modify_payload
    )
    assert modify_resp.status_code == 200

    # 5. Check balance again, costo_base_matricula should be 700,000 (850k - 150k discount)
    balance_resp = client.get(
        f"/api/v1/enrollment/students/{student.id}/balance?year=2026"
    )
    balance_data = balance_resp.json()
    assert balance_data["costo_base_matricula"] == 700000
    assert balance_data["pendiente_base"] == 700000
    assert balance_data["total_pendiente"] == 700000

    # 6. Make a partial payment to base cost, say 200,000
    pay_payload = {
        "matricula_id": matricula_id,
        "asignaciones": [{"concepto": "matricula_base", "monto": 200000}],
        "codigo_talonario": "TAL-TEST-100",
        "observacion": "Abono base",
    }
    pay_resp = client.post("/api/v1/enrollment/payments/directed", json=pay_payload)
    assert pay_resp.status_code == 201

    # 7. Check balance again. base_cost should still be 700,000, and base_paid should be 200,000, pending_base 500,000.
    balance_resp = client.get(
        f"/api/v1/enrollment/students/{student.id}/balance?year=2026"
    )
    balance_data = balance_resp.json()
    assert balance_data["costo_base_matricula"] == 700000
    assert balance_data["pendiente_base"] == 500000
    assert balance_data["total_pagado"] == 200000
    assert balance_data["total_pendiente"] == 500000


def test_filter_complementaries_catalog(session, client):
    # 1. Create different types of complementaries
    tipo_matricula = TipoComplementario(nombre="Matricula", estado=True)
    session.add(tipo_matricula)
    session.flush()

    tipo_deporte = TipoComplementario(
        nombre="Deportes", estado=True, sub_tipo_complementario=tipo_matricula.id
    )
    session.add(tipo_deporte)
    session.flush()

    tipo_externo = TipoComplementario(nombre="Pruebas Internas", estado=True)
    session.add(tipo_externo)
    session.flush()

    comp_seguro = Complementario(
        nombre="Seguro Matricula",
        tipo_complementario_id=tipo_matricula.id,
        anio=2026,
        valor=120000,
        estado_complemento="Activo",
    )
    comp_futbol = Complementario(
        nombre="Escuela Futbol (Deporte)",
        tipo_complementario_id=tipo_deporte.id,
        anio=2026,
        valor=60000,
        estado_complemento="Activo",
    )
    comp_externo = Complementario(
        nombre="Prueba Saber 11 Externo",
        tipo_complementario_id=tipo_externo.id,
        anio=2026,
        valor=45000,
        estado_complemento="Activo",
    )
    session.add_all([comp_seguro, comp_futbol, comp_externo])
    session.commit()

    # 2. Get complementaries catalog from enrollment module
    resp = client.get("/api/v1/enrollment/complementary?year=2026")
    assert resp.status_code == 200
    catalog = resp.json()

    # Only "Seguro Matricula" and "Escuela Futbol (Deporte)" should be returned.
    # "Prueba Saber 11 Externo" should NOT be returned.
    names = [c["tipo_complementario"] for c in catalog]
    assert "Seguro Matricula" in names
    assert "Escuela Futbol (Deporte)" in names
    assert "Prueba Saber 11 Externo" not in names


def test_create_complementary_default_behavior(session, client):
    # 1. Create a complementary without specifying type (default behavior: links to "Matricula")
    payload = {
        "nombre": "Carnet Estudiantil",
        "anio": 2026,
        "valor": 15000,
        "estado_complemento": "Activo",
    }
    resp = client.post("/api/v1/enrollment/complementary", json=payload)
    assert resp.status_code == 201
    comp_id = resp.json()["complementario_id"]

    # 2. Check catalog: Carnet should be returned
    cat_resp = client.get("/api/v1/enrollment/complementary?year=2026")
    catalog = cat_resp.json()

    carnet = next(c for c in catalog if c["id"] == comp_id)
    assert carnet["tipo_complementario"] == "Carnet Estudiantil"

    # 3. Verify that new enrollments auto-assign it
    grado = Grado(nombre="Primero")
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
        nombre="Acudiente Primero",
        parentesco="Madre",
        telefono="3112223344",
        correo="carlos@gmail.com",
    )
    session.add(acudiente)
    session.commit()
    session.refresh(acudiente)

    student = Estudiante(
        nombre="Estudiante Primero",
        documento="1005111111",
        grado_id=grado.id,
        acudiente_id=acudiente.id,
        activo=True,
    )
    session.add(student)
    session.commit()
    session.refresh(student)

    param_mat = ParametrizarMatricula(grado_id=grado.id or 1, anio=2026, valor=600000)
    session.add(param_mat)
    session.commit()

    reg_payload = {
        "estudiante_id": student.id,
        "periodo_id": periodo.id,
        "anio": 2026,
    }
    reg_resp = client.post("/api/v1/enrollment/register", json=reg_payload)
    assert reg_resp.status_code == status.HTTP_201_CREATED
    reg_data = reg_resp.json()

    # The enrollment total value should include the tuition base (600k) + Carnet (15k) = 615k.
    assert reg_data["valor_total"] == 615000
    assert reg_data["total_complementarios"] == 15000
    assert len(reg_data["complementarios"]) == 1
    assert reg_data["complementarios"][0]["complementario_id"] == comp_id
