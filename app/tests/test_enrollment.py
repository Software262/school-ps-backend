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


def test_student_search_and_payment_count(session, client):
    # 1. Seed base data
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
    session.commit()
    session.refresh(estudiante)

    # Seed parametrization and period
    periodo = Periodo(
        periodo_electivo=datetime.now(), estado=True, fecha=datetime.now()
    )
    session.add(periodo)
    session.commit()
    session.refresh(periodo)

    param = ParametrizarMatricula(grado_id=grado.id, anio=2026, valor=1500000)
    session.add(param)
    session.commit()
    session.refresh(param)

    # 2. Test search when student has no active enrollment
    response = client.get(
        "/api/v1/enrollment/students", params={"nombre": "felipe", "year": 2026}
    )
    assert response.status_code == status.HTTP_200_OK
    json_data = response.json()
    assert json_data["total_resultados"] == 1
    student_item = json_data["estudiantes"][0]
    assert student_item["nombre"] == "Felipe Gomez"
    assert student_item["documento"] == "10987654321"
    assert student_item["matricula_registrada"] is False
    assert student_item["estado_matricula"] == "sin_matricula"
    assert student_item["pagos_realizados"] == 0
    assert student_item["saldo_pendiente"] == 1500000

    # Test search filtering by document/code
    response_doc = client.get(
        "/api/v1/enrollment/students", params={"documento": "10987", "year": 2026}
    )
    assert response_doc.status_code == status.HTTP_200_OK
    assert response_doc.json()["total_resultados"] == 1

    response_no_match = client.get(
        "/api/v1/enrollment/students", params={"nombre": "Nonexistent", "year": 2026}
    )
    assert response_no_match.status_code == status.HTTP_200_OK
    assert response_no_match.json()["total_resultados"] == 0

    # 3. Test register enrollment
    register_payload = {
        "estudiante_id": estudiante.id,
        "periodo_id": periodo.id,
        "anio": 2026,
    }
    resp_reg = client.post("/api/v1/enrollment/register", json=register_payload)
    assert resp_reg.status_code == status.HTTP_201_CREATED
    matricula_id = resp_reg.json()["matricula_id"]

    # 4. Test search after registration
    response_after = client.get(
        "/api/v1/enrollment/students", params={"nombre": "Felipe", "year": 2026}
    )
    assert response_after.status_code == status.HTTP_200_OK
    student_item_after = response_after.json()["estudiantes"][0]
    assert student_item_after["matricula_registrada"] is True
    assert student_item_after["estado_matricula"] == "sin_abono"
    assert student_item_after["pagos_realizados"] == 0
    assert student_item_after["saldo_pendiente"] == 1500000

    # 5. Test get_enrollment_balance shows pagos_realizados = 0
    resp_bal = client.get(
        f"/api/v1/enrollment/students/{estudiante.id}/balance", params={"year": 2026}
    )
    assert resp_bal.status_code == status.HTTP_200_OK
    assert resp_bal.json()["pagos_realizados"] == 0

    # 6. Test making a payment and verifying that pagos_realizados increases
    # We will register a directed payment
    payment_payload = {
        "matricula_id": matricula_id,
        "codigo_talonario": "TAL-12345",
        "observacion": "Primer abono",
        "asignaciones": [{"concepto": "matricula_base", "monto": 500000}],
    }
    resp_pay = client.post("/api/v1/enrollment/payments/directed", json=payment_payload)
    assert resp_pay.status_code == status.HTTP_201_CREATED

    # Now verify updated balance and search results
    resp_bal2 = client.get(
        f"/api/v1/enrollment/students/{estudiante.id}/balance", params={"year": 2026}
    )
    assert resp_bal2.status_code == status.HTTP_200_OK
    assert resp_bal2.json()["pagos_realizados"] == 1
    assert resp_bal2.json()["total_pendiente"] == 1000000
    assert resp_bal2.json()["total_pagado"] == 500000
    assert resp_bal2.json()["estado_matricula"] == "parcial"

    response_search2 = client.get(
        "/api/v1/enrollment/students", params={"nombre": "Felipe", "year": 2026}
    )
    assert response_search2.status_code == status.HTTP_200_OK
    student_item2 = response_search2.json()["estudiantes"][0]
    assert student_item2["matricula_registrada"] is True
    assert student_item2["estado_matricula"] == "parcial"
    assert student_item2["pagos_realizados"] == 1
    assert student_item2["saldo_pendiente"] == 1000000
