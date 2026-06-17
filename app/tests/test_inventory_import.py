"""Pruebas para la subida masiva de inventario (CSV/Excel) con upsert.

Cubre cuatro niveles:
- Parser/validación del archivo (``utils.file``): errores controlados por fila.
- Upsert real contra una base SQLite en memoria (``InventoryRepository``).
- Orquestación y resumen de resultados (``InventoryService.import_items``).
- Endpoints HTTP: descarga de plantilla e importación end-to-end.
"""

from tempfile import SpooledTemporaryFile
from typing import BinaryIO, cast
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import UploadFile
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, col, create_engine, select
from starlette.datastructures import Headers

from app.core.db import get_session
from app.main import app
from app.modules.inventory.domain.service import InventoryService
from app.modules.inventory.infrastructure.models import (
    EstadoInventario,
    Inventario,
    InventarioStock,
    TipoInventario,
)
from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.inventory.schemas.request import InventoryItemRequest
from app.modules.inventory.schemas.response import ImportRowError
from app.modules.inventory.utils.file import validate_data, validate_file

CSV_CONTENT_TYPE = "text/csv"
XLSX_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
IMPORT_URL = "/api/v1/inventory/items/import"
TEMPLATE_URL = "/api/v1/inventory/items/template"


def _upload(
    content: bytes,
    filename: str | None = "items.csv",
    content_type: str = CSV_CONTENT_TYPE,
) -> UploadFile:
    buffer = SpooledTemporaryFile()
    buffer.write(content)
    buffer.seek(0)
    return UploadFile(
        file=cast(BinaryIO, buffer),
        filename=filename,
        headers=Headers({"content-type": content_type}),
    )


# --------------------------------------------------------------------------- #
# utils.file -> validate_file
# --------------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_validate_file_accepts_csv():
    upload = _upload(b"col\n1")
    assert await validate_file(upload) == b"col\n1"


@pytest.mark.asyncio
async def test_validate_file_rejects_unsupported_content_type():
    upload = _upload(b"x", filename="items.pdf", content_type="application/pdf")
    assert await validate_file(upload) is None


@pytest.mark.asyncio
async def test_validate_file_rejects_missing_filename():
    upload = _upload(b"x", filename=None)
    assert await validate_file(upload) is None


# --------------------------------------------------------------------------- #
# utils.file -> validate_data
# --------------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_validate_data_parses_valid_rows_and_optional_stocks():
    csv = (
        b"tipo_inventario,nombre,cantidad_total,observacion,"
        b"cantidad_disponible,cantidad_mantenimiento\n"
        b"banda,Trompeta,10,buena,8,2\n"
        b"banda,Tambor,5,,,\n"
    )
    valid, errors = await validate_data("items.csv", csv)

    assert errors == []
    assert [row for row, _ in valid] == [2, 3]

    trompeta = valid[0][1]
    assert trompeta.tipo_inventario == "banda"
    assert trompeta.nombre == "Trompeta"
    assert trompeta.cantidad_disponible == 8
    assert trompeta.cantidad_mantenimiento == 2

    tambor = valid[1][1]
    # Las columnas vacías (NaN) se normalizan a None, no a 0 ni NaN.
    assert tambor.observacion is None
    assert tambor.cantidad_disponible is None
    assert tambor.cantidad_mantenimiento is None


@pytest.mark.asyncio
async def test_validate_data_reports_missing_required_columns():
    csv = b"nombre,cantidad_total\nTrompeta,5\n"
    valid, errors = await validate_data("items.csv", csv)

    assert valid == []
    assert len(errors) == 1
    assert "tipo_inventario" in errors[0].error


@pytest.mark.asyncio
async def test_validate_data_collects_per_row_errors_without_aborting():
    csv = (
        b"tipo_inventario,nombre,cantidad_total\n"
        b"banda,Valido,5\n"  # fila 2 ok
        b"tenis,MalTipo,3\n"  # fila 3: tipo_inventario fuera del Literal
        b"banda,X,abc\n"  # fila 4: nombre corto + cantidad no numérica
        b"banda,OtroValido,4\n"  # fila 5 ok
    )
    valid, errors = await validate_data("items.csv", csv)

    assert [row for row, _ in valid] == [2, 5]
    assert {e.row for e in errors} == {3, 4}

    error_by_row = {e.row: e for e in errors}
    assert "tipo_inventario" in error_by_row[3].error
    assert "nombre" in error_by_row[4].error
    assert "cantidad_total" in error_by_row[4].error


@pytest.mark.asyncio
async def test_validate_data_detects_in_file_duplicates_case_insensitive():
    csv = (
        b"tipo_inventario,nombre,cantidad_total\n"
        b"banda,Trompeta,10\n"
        b"banda,trompeta,5\n"  # duplicado (case-insensitive)
    )
    valid, errors = await validate_data("items.csv", csv)

    assert len(valid) == 1
    assert len(errors) == 1
    assert errors[0].row == 3
    assert "duplicado" in errors[0].error.lower()


@pytest.mark.asyncio
async def test_validate_data_empty_file_returns_nothing():
    csv = b"tipo_inventario,nombre,cantidad_total\n"
    valid, errors = await validate_data("items.csv", csv)
    assert valid == []
    assert errors == []


# --------------------------------------------------------------------------- #
# InventoryService.upsert_imported_item  (SQLite en memoria)
# --------------------------------------------------------------------------- #


@pytest.fixture
def session():
    """Sesión SQLite en memoria con las tablas y datos semilla de inventario."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    tables = [
        SQLModel.metadata.tables[name]
        for name in (
            "tipoinventario",
            "estadoinventario",
            "inventario",
            "inventariostock",
        )
    ]
    SQLModel.metadata.create_all(engine, tables=tables)

    with Session(engine) as db:
        db.add_all(
            [
                EstadoInventario(nombre="disponible"),
                EstadoInventario(nombre="prestado"),
                EstadoInventario(nombre="mantenimiento"),
                TipoInventario(nombre="banda"),
                TipoInventario(nombre="ajedrez"),
                # "deporte" se deja sin sembrar a propósito para validar el
                # control de tipo inexistente en la base de datos.
            ]
        )
        db.commit()
        yield db


def _real_service(session: Session) -> InventoryService:
    """Servicio con repositorio real (SQLite) y enrollment irrelevante al import."""
    return InventoryService(
        repository=InventoryRepository(session=session),
        enrollment=MagicMock(),
    )


def _stocks(session: Session, item_id: int) -> dict[str, int]:
    rows = session.exec(
        select(InventarioStock, EstadoInventario).join(
            EstadoInventario,
            col(InventarioStock.estado_inventario_id) == col(EstadoInventario.id),
        )
    ).all()
    return {
        state.nombre: stock.cantidad
        for stock, state in rows
        if stock.inventario_id == item_id
    }


@pytest.mark.asyncio
async def test_upsert_creates_new_item_with_default_stock(session):
    service = _real_service(session)

    result = await service.upsert_imported_item(
        InventoryItemRequest(
            tipo_inventario="banda", nombre="Trompeta", cantidad_total=10
        )
    )

    assert result == "created"
    item = session.exec(select(Inventario)).one()
    assert item.nombre == "Trompeta"
    assert item.cantidad_total == 10
    # Sin stocks explícitos: todo va a "disponible".
    assert _stocks(session, item.id) == {
        "disponible": 10,
        "mantenimiento": 0,
        "prestado": 0,
    }


@pytest.mark.asyncio
async def test_upsert_creates_new_item_with_explicit_stock_distribution(session):
    service = _real_service(session)

    result = await service.upsert_imported_item(
        InventoryItemRequest(
            tipo_inventario="banda",
            nombre="Tambor",
            cantidad_total=10,
            cantidad_disponible=7,
            cantidad_mantenimiento=3,
        )
    )

    assert result == "created"
    item = session.exec(select(Inventario)).one()
    assert _stocks(session, item.id) == {
        "disponible": 7,
        "mantenimiento": 3,
        "prestado": 0,
    }


@pytest.mark.asyncio
async def test_upsert_updates_existing_item_preserving_borrowed(session):
    service = _real_service(session)

    # Crea y luego marca 4 como prestados manualmente.
    await service.upsert_imported_item(
        InventoryItemRequest(
            tipo_inventario="banda", nombre="Flauta", cantidad_total=10
        )
    )
    item = session.exec(select(Inventario)).one()
    await service.repository.set_amount_stock_category(item.id, 6, "disponible")
    await service.repository.set_amount_stock_category(item.id, 4, "prestado")

    # Reimporta el mismo nombre subiendo el total: lo existente debe ACTUALIZARSE.
    result = await service.upsert_imported_item(
        InventoryItemRequest(
            tipo_inventario="banda",
            nombre="Flauta",
            cantidad_total=12,
            cantidad_mantenimiento=2,
        )
    )

    assert result == "updated"
    assert session.exec(select(Inventario)).one().cantidad_total == 12
    # prestado se respeta (4); disponible se recalcula: 12 - 4 - 2 = 6.
    assert _stocks(session, item.id) == {
        "disponible": 6,
        "mantenimiento": 2,
        "prestado": 4,
    }
    # No se crea un segundo registro.
    assert len(session.exec(select(Inventario)).all()) == 1


@pytest.mark.asyncio
async def test_upsert_matches_existing_case_insensitively(session):
    service = _real_service(session)

    await service.upsert_imported_item(
        InventoryItemRequest(
            tipo_inventario="banda", nombre="Trompeta", cantidad_total=5
        )
    )
    result = await service.upsert_imported_item(
        InventoryItemRequest(
            tipo_inventario="banda", nombre="trompeta", cantidad_total=8
        )
    )

    assert result == "updated"
    assert len(session.exec(select(Inventario)).all()) == 1


@pytest.mark.asyncio
async def test_upsert_rejects_unknown_type(session):
    service = _real_service(session)

    with pytest.raises(ValueError, match="tipo de inventario"):
        await service.upsert_imported_item(
            InventoryItemRequest(
                tipo_inventario="deporte", nombre="Trompeta", cantidad_total=5
            )
        )


@pytest.mark.asyncio
async def test_upsert_rejects_inconsistent_stock_sum_on_create(session):
    service = _real_service(session)

    with pytest.raises(ValueError, match="cantidad total"):
        await service.upsert_imported_item(
            InventoryItemRequest(
                tipo_inventario="banda",
                nombre="Trompeta",
                cantidad_total=10,
                cantidad_disponible=5,
                cantidad_mantenimiento=2,  # 5 + 2 != 10
            )
        )

    # Nada debe haberse persistido tras el error.
    assert session.exec(select(Inventario)).all() == []


@pytest.mark.asyncio
async def test_upsert_rejects_total_below_borrowed_on_update(session):
    service = _real_service(session)

    await service.upsert_imported_item(
        InventoryItemRequest(
            tipo_inventario="banda", nombre="Flauta", cantidad_total=10
        )
    )
    item = session.exec(select(Inventario)).one()
    await service.repository.set_amount_stock_category(item.id, 5, "disponible")
    await service.repository.set_amount_stock_category(item.id, 5, "prestado")

    # total=3 es menor que lo prestado (5) -> disponible quedaría negativo.
    with pytest.raises(ValueError, match="negativa"):
        await service.upsert_imported_item(
            InventoryItemRequest(
                tipo_inventario="banda", nombre="Flauta", cantidad_total=3
            )
        )


# --------------------------------------------------------------------------- #
# InventoryService.import_items  (orquestación)
# --------------------------------------------------------------------------- #


def _service_with_mock_repo() -> tuple[InventoryService, MagicMock, AsyncMock]:
    """Aisla ``import_items`` mockeando el upsert por fila (ya en el servicio).

    La orquestacion solo depende de ``service.upsert_imported_item`` (resultado
    o excepcion) y de ``repository.rollback``; el resto del repositorio no se
    toca. Devuelve tambien el ``AsyncMock`` del upsert para configurarlo e
    inspeccionarlo sin pelear con el tipado del metodo real.
    """
    repo = MagicMock()
    repo.rollback = MagicMock()
    service = InventoryService(repository=repo, enrollment=MagicMock())
    upsert = AsyncMock()
    service.upsert_imported_item = upsert  # type: ignore[method-assign]
    return service, repo, upsert


@pytest.mark.asyncio
async def test_import_items_summarizes_created_and_updated():
    service, repo, upsert = _service_with_mock_repo()
    upsert.side_effect = ["created", "updated", "created"]

    valid = [
        (
            2,
            InventoryItemRequest(
                tipo_inventario="banda", nombre="AA", cantidad_total=1
            ),
        ),
        (
            3,
            InventoryItemRequest(
                tipo_inventario="banda", nombre="BB", cantidad_total=1
            ),
        ),
        (
            4,
            InventoryItemRequest(
                tipo_inventario="banda", nombre="CC", cantidad_total=1
            ),
        ),
    ]

    result = await service.import_items(valid_items=valid, parse_errors=[])

    assert result.total == 3
    assert result.created == 2
    assert result.updated == 1
    assert result.failed == 0
    assert result.errors == []
    repo.rollback.assert_not_called()


@pytest.mark.asyncio
async def test_import_items_handles_row_errors_and_rolls_back():
    service, repo, upsert = _service_with_mock_repo()
    upsert.side_effect = [
        "created",
        ValueError("stock inconsistente"),
        RuntimeError("boom inesperado"),
    ]

    valid = [
        (
            2,
            InventoryItemRequest(
                tipo_inventario="banda", nombre="AA", cantidad_total=1
            ),
        ),
        (
            3,
            InventoryItemRequest(
                tipo_inventario="banda", nombre="BB", cantidad_total=1
            ),
        ),
        (
            4,
            InventoryItemRequest(
                tipo_inventario="banda", nombre="CC", cantidad_total=1
            ),
        ),
    ]

    result = await service.import_items(valid_items=valid, parse_errors=[])

    assert result.created == 1
    assert result.updated == 0
    assert result.failed == 2
    assert repo.rollback.call_count == 2

    errors_by_row = {e.row: e for e in result.errors}
    assert errors_by_row[3].error == "stock inconsistente"
    # Las excepciones inesperadas se reportan con un mensaje genérico.
    assert errors_by_row[4].error == "Error inesperado al procesar la fila"


@pytest.mark.asyncio
async def test_import_items_merges_parse_errors_into_summary():
    service, repo, upsert = _service_with_mock_repo()
    upsert.side_effect = ["created"]

    valid = [
        (
            2,
            InventoryItemRequest(
                tipo_inventario="banda", nombre="AA", cantidad_total=1
            ),
        ),
    ]
    parse_errors = [
        ImportRowError(row=5, nombre="Mala", error="cantidad_total inválida")
    ]

    result = await service.import_items(valid_items=valid, parse_errors=parse_errors)

    assert result.total == 2  # 1 válida + 1 con error de parseo
    assert result.created == 1
    assert result.failed == 1
    assert result.errors[0].row == 5


# --------------------------------------------------------------------------- #
# Endpoints HTTP  (TestClient con sesión SQLite inyectada)
# --------------------------------------------------------------------------- #


@pytest.fixture
def client(session):
    """TestClient con ``get_session`` apuntando a la base SQLite de prueba."""

    def _override_get_session():
        yield session

    app.dependency_overrides[get_session] = _override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_session, None)


def test_download_template_xlsx_by_default(client):
    response = client.get(TEMPLATE_URL)

    assert response.status_code == 200
    assert response.headers["content-type"] == XLSX_CONTENT_TYPE
    assert "plantilla_inventario.xlsx" in response.headers["content-disposition"]
    assert response.content  # archivo no vacío


def test_download_template_csv(client):
    response = client.get(TEMPLATE_URL, params={"format": "csv"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(CSV_CONTENT_TYPE)
    assert "plantilla_inventario.csv" in response.headers["content-disposition"]
    assert b"tipo_inventario" in response.content


def test_download_template_rejects_invalid_format(client):
    response = client.get(TEMPLATE_URL, params={"format": "pdf"})
    assert response.status_code == 422


def test_template_is_reimportable_end_to_end(client, session):
    # 1) Se descarga la plantilla...
    template = client.get(TEMPLATE_URL, params={"format": "csv"})
    assert template.status_code == 200

    # 2) ...y se vuelve a subir tal cual al endpoint de importación.
    response = client.post(
        IMPORT_URL,
        files={
            "file": ("plantilla_inventario.csv", template.content, CSV_CONTENT_TYPE)
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["created"] == 2  # Trompeta (banda) y Tablero (ajedrez)
    assert body["data"]["failed"] == 0

    nombres = {item.nombre for item in session.exec(select(Inventario)).all()}
    assert nombres == {"Trompeta", "Tablero"}


def test_import_endpoint_rejects_invalid_file_type(client):
    response = client.post(
        IMPORT_URL,
        files={"file": ("notas.pdf", b"contenido", "application/pdf")},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert "csv o excel" in body["message"]


def test_import_endpoint_reports_per_row_errors(client):
    csv = (
        b"tipo_inventario,nombre,cantidad_total\n"
        b"banda,Trompeta,10\n"  # ok -> created
        b"deporte,SinTipo,5\n"  # tipo válido pero no existe en DB -> error de fila
    )
    response = client.post(
        IMPORT_URL,
        files={"file": ("items.csv", csv, CSV_CONTENT_TYPE)},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert body["data"]["created"] == 1
    assert body["data"]["failed"] == 1
    assert body["data"]["errors"][0]["nombre"] == "SinTipo"


# --------------------------------------------------------------------------- #
# Restricción de tipo por módulo (banda / deporte)
# --------------------------------------------------------------------------- #

BAND_IMPORT_URL = "/api/v1/musical-band/items/import"
BAND_TEMPLATE_URL = "/api/v1/musical-band/items/template"
SPORT_IMPORT_URL = "/api/v1/sports/items/import"
SPORT_TEMPLATE_URL = "/api/v1/sports/items/template"


@pytest.mark.asyncio
async def test_import_items_rejects_rows_of_other_type():
    """``allowed_type`` descarta filas de otro tipo sin tocar el repositorio."""
    service, repo, upsert = _service_with_mock_repo()
    upsert.side_effect = ["created"]

    valid = [
        (
            2,
            InventoryItemRequest(
                tipo_inventario="banda", nombre="Trompeta", cantidad_total=1
            ),
        ),
        (
            3,
            InventoryItemRequest(
                tipo_inventario="deporte", nombre="Balon", cantidad_total=1
            ),
        ),
    ]

    result = await service.import_items(
        valid_items=valid, parse_errors=[], allowed_type="banda"
    )

    assert result.created == 1
    assert result.failed == 1
    # La fila de deporte ni siquiera se intenta persistir.
    assert upsert.await_count == 1
    error = result.errors[0]
    assert error.nombre == "Balon"
    assert "deporte" in error.error and "banda" in error.error


def test_band_import_endpoint_assigns_band_without_type_column(client, session):
    # El archivo del modulo de banda no necesita la columna ``tipo_inventario``:
    # todo lo que se sube a este endpoint es de tipo banda.
    csv = b"nombre,cantidad_total\nTrompeta,10\nTambor,5\n"
    response = client.post(
        BAND_IMPORT_URL,
        files={"file": ("items.csv", csv, CSV_CONTENT_TYPE)},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["created"] == 2
    assert body["data"]["failed"] == 0

    nombres = {item.nombre for item in session.exec(select(Inventario)).all()}
    assert nombres == {"Trompeta", "Tambor"}


def test_band_import_endpoint_overrides_type_column(client, session):
    # Si el archivo trae ``tipo_inventario``, el endpoint lo ignora y fuerza banda.
    csv = (
        b"tipo_inventario,nombre,cantidad_total\n"
        b"deporte,Trompeta,10\n"  # el tipo del archivo se sobreescribe a banda
    )
    response = client.post(
        BAND_IMPORT_URL,
        files={"file": ("items.csv", csv, CSV_CONTENT_TYPE)},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["created"] == 1
    assert body["data"]["failed"] == 0

    item = session.exec(select(Inventario)).one()
    banda_id = session.exec(
        select(TipoInventario.id).where(TipoInventario.nombre == "banda")
    ).one()
    assert item.tipo_inventario_id == banda_id


def test_sport_import_endpoint_assigns_sport_without_type_column(client, session):
    # ``deporte`` no se siembra en la fixture; lo agregamos para este caso.
    session.add(TipoInventario(nombre="deporte"))
    session.commit()

    csv = b"nombre,cantidad_total\nBalon,15\n"
    response = client.post(
        SPORT_IMPORT_URL,
        files={"file": ("items.csv", csv, CSV_CONTENT_TYPE)},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["created"] == 1
    assert body["data"]["failed"] == 0

    item = session.exec(select(Inventario)).one()
    deporte_id = session.exec(
        select(TipoInventario.id).where(TipoInventario.nombre == "deporte")
    ).one()
    assert item.tipo_inventario_id == deporte_id


def test_band_template_endpoint_omits_type_column(client):
    response = client.get(BAND_TEMPLATE_URL, params={"format": "csv"})

    assert response.status_code == 200
    assert "plantilla_inventario_banda.csv" in response.headers["content-disposition"]
    # El tipo lo fija el endpoint: la plantilla del modulo no trae la columna.
    assert b"tipo_inventario" not in response.content
    assert b"Trompeta" in response.content
    assert b"deporte" not in response.content


def test_sport_template_endpoint_omits_type_column(client):
    response = client.get(SPORT_TEMPLATE_URL, params={"format": "csv"})

    assert response.status_code == 200
    assert "plantilla_inventario_deporte.csv" in response.headers["content-disposition"]
    assert b"tipo_inventario" not in response.content
    assert b"Balon de futbol" in response.content
    assert b"banda" not in response.content
