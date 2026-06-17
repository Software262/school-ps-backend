import pytest
from datetime import datetime
from sqlmodel import SQLModel, Session, create_engine, select
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.db import get_session
from app.modules.inventory.infrastructure.models import (
    EstadoInventario,
    Inventario,
    InventarioStock,
    TipoInventario,
)
from app.modules.enrollment.infrastructure.models import Estudiante, Grado, Acudiente

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture(name="session")
def session_fixture():
    # Create all tables (including inventory, chess, and student)
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine, expire_on_commit=False) as session:
        # Seed required states and type
        disp = EstadoInventario(nombre="disponible")
        prest = EstadoInventario(nombre="prestado")
        mant = EstadoInventario(nombre="mantenimiento")
        tipo = TipoInventario(nombre="ajedrez")

        # Seed student relationships to avoid IntegrityErrors
        grado = Grado(nombre="Décimo")
        acudiente = Acudiente(
            nombre="Carlos Gomez",
            parentesco="Padre",
            telefono="3112223344",
            correo="carlos@gmail.com",
        )
        session.add_all([disp, prest, mant, tipo, grado, acudiente])
        session.commit()
        session.refresh(grado)
        session.refresh(acudiente)

        estudiante = Estudiante(
            nombre="Estudiante Prueba",
            documento="987654321",
            grado_id=grado.id,
            acudiente_id=acudiente.id,
            activo=True,
        )
        session.add(estudiante)
        session.commit()
        yield session
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture(name="client")
def client_fixture(session):
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_create_chess_item_with_custom_pieces(session, client):
    tipo = session.exec(
        select(TipoInventario).where(TipoInventario.nombre == "ajedrez")
    ).one()
    payload = {
        "tipo_inventario_id": tipo.id,
        "nombre": "Tablero Premium",
        "cantidad_total": 5,
        "observacion": "Alta calidad",
        "piezas_totales": 16,
    }
    response = client.post("/api/v1/chess/items", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    json_data = response.json()
    assert json_data["statusCode"] == 201
    assert json_data["data"]["piezas_totales"] == 16

    # Verify database state
    item = session.exec(
        select(Inventario).where(Inventario.nombre == "Tablero Premium")
    ).one()
    assert item.observacion == "[PIEZAS:16] Alta calidad"
    assert item.cantidad_total == 5


def test_return_chess_borrow_incomplete_and_resolve(session, client):
    tipo = session.exec(
        select(TipoInventario).where(TipoInventario.nombre == "ajedrez")
    ).one()
    estudiante = session.exec(select(Estudiante)).one()

    # Create chess item
    item_payload = {
        "tipo_inventario_id": tipo.id,
        "nombre": "Tablero Pro",
        "cantidad_total": 1,
        "observacion": "Para torneos",
        "piezas_totales": 32,
    }
    item_res = client.post("/api/v1/chess/items", json=item_payload)
    assert item_res.status_code == status.HTTP_201_CREATED
    item_id = item_res.json()["data"]["id"]

    # Borrow the item
    borrow_payload = {
        "inventario_id": item_id,
        "estudiante_id": estudiante.id,
        "fecha_salida": datetime.now().isoformat(),
        "cantidad": 1,
        "observacion": "Prestamo torneo",
    }
    borrow_res = client.post("/api/v1/chess/borrow", json=borrow_payload)
    assert borrow_res.status_code == status.HTTP_201_CREATED
    prestamo_id = borrow_res.json()["data"]["prestamo_id"]

    # Verify stock: disponible = 0, prestado = 1, mantenimiento = 0
    disp_state = session.exec(
        select(EstadoInventario).where(EstadoInventario.nombre == "disponible")
    ).one()
    prest_state = session.exec(
        select(EstadoInventario).where(EstadoInventario.nombre == "prestado")
    ).one()
    mant_state = session.exec(
        select(EstadoInventario).where(EstadoInventario.nombre == "mantenimiento")
    ).one()

    stock_disp = session.exec(
        select(InventarioStock).where(
            InventarioStock.inventario_id == item_id,
            InventarioStock.estado_inventario_id == disp_state.id,
        )
    ).one()
    stock_prest = session.exec(
        select(InventarioStock).where(
            InventarioStock.inventario_id == item_id,
            InventarioStock.estado_inventario_id == prest_state.id,
        )
    ).one()
    stock_mant = session.exec(
        select(InventarioStock).where(
            InventarioStock.inventario_id == item_id,
            InventarioStock.estado_inventario_id == mant_state.id,
        )
    ).one()

    assert stock_disp.cantidad == 0
    assert stock_prest.cantidad == 1
    assert stock_mant.cantidad == 0

    # Return incomplete: 30 pieces returned instead of 32
    return_payload = {
        "conteo_piezas": 30,
        "observacion": "Faltan 2 peones",
    }
    return_res = client.post(f"/api/v1/chess/return/{prestamo_id}", json=return_payload)
    assert return_res.status_code == status.HTTP_200_OK
    assert return_res.json()["data"]["novedad_creada"] is True

    # Verify stock: disponible = 0, prestado = 0, mantenimiento = 1
    session.expire_all()
    stock_disp = session.exec(
        select(InventarioStock).where(
            InventarioStock.inventario_id == item_id,
            InventarioStock.estado_inventario_id == disp_state.id,
        )
    ).one()
    stock_prest = session.exec(
        select(InventarioStock).where(
            InventarioStock.inventario_id == item_id,
            InventarioStock.estado_inventario_id == prest_state.id,
        )
    ).one()
    stock_mant = session.exec(
        select(InventarioStock).where(
            InventarioStock.inventario_id == item_id,
            InventarioStock.estado_inventario_id == mant_state.id,
        )
    ).one()

    assert stock_disp.cantidad == 0
    assert stock_prest.cantidad == 0
    assert stock_mant.cantidad == 1

    # Resolve novelty
    resolve_payload = {
        "notas_resolucion": "Se repusieron los 2 peones faltantes",
        "usuario_auditoria_id": 1,
    }
    resolve_res = client.post(
        f"/api/v1/chess/borrow/{prestamo_id}/resolve-novelty", json=resolve_payload
    )
    assert resolve_res.status_code == status.HTTP_200_OK

    # Verify stock: disponible = 1, prestado = 0, mantenimiento = 0
    session.expire_all()
    stock_disp = session.exec(
        select(InventarioStock).where(
            InventarioStock.inventario_id == item_id,
            InventarioStock.estado_inventario_id == disp_state.id,
        )
    ).one()
    stock_prest = session.exec(
        select(InventarioStock).where(
            InventarioStock.inventario_id == item_id,
            InventarioStock.estado_inventario_id == prest_state.id,
        )
    ).one()
    stock_mant = session.exec(
        select(InventarioStock).where(
            InventarioStock.inventario_id == item_id,
            InventarioStock.estado_inventario_id == mant_state.id,
        )
    ).one()

    assert stock_disp.cantidad == 1
    assert stock_prest.cantidad == 0
    assert stock_mant.cantidad == 0
