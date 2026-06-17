from typing import Annotated, Any
from fastapi import APIRouter, Query, status
from app.core.db import SessionDep
from app.modules.inventory.application.get_items_inventory import GetItemsInventory
from app.modules.inventory.application.get_borrowings import GetBorrowings
from app.modules.inventory.schemas.request import (
    FilterPaginationInventory,
    FilterPaginationBorrowings,
)
from app.shared.utils.response import Response

from app.modules.chess.schemas.request import (
    CreateChessBorrowRequest,
    ReturnChessBorrowRequest,
    ResolveChessNoveltyRequest,
    ResolveBorrowNoveltyRequest,
    CreateChessItemRequest,
)

from app.modules.chess.application.create_borrowing import CreateChessBorrowing
from app.modules.chess.application.return_borrowing import ReturnChessBorrowing
from app.modules.chess.application.resolve_novelty import ResolveChessNovelty
from app.modules.chess.application.resolve_borrow_novelty import ResolveBorrowNovelty
from app.modules.chess.application.get_clearance import GetChessClearance
from app.modules.chess.application.create_item import CreateChessItem

router = APIRouter()


@router.post("/borrow", status_code=status.HTTP_201_CREATED)
async def create_chess_borrow(
    session: SessionDep, request_data: CreateChessBorrowRequest
):
    app_service = CreateChessBorrowing(session=session)
    result = await app_service.execute(request_data)

    if isinstance(result, dict) and result.get("error"):
        status_code = (
            status.HTTP_404_NOT_FOUND
            if result["error"] == "NOT_FOUND"
            else status.HTTP_400_BAD_REQUEST
        )
        return Response(
            data=None,
            message="Error al registrar el préstamo",
            status_code=status_code,
            details={"error": result["message"]},
        ).to_dict()

    return Response(
        data={"prestamo_id": getattr(result, "id", None)},
        message="Préstamo de ajedrez registrado exitosamente.",
        status_code=status.HTTP_201_CREATED,
    ).to_dict()


@router.post("/return/{prestamo_id}", status_code=status.HTTP_200_OK)
async def return_chess_borrow(
    session: SessionDep, prestamo_id: int, request_data: ReturnChessBorrowRequest
):
    user_id = 1
    app_service = ReturnChessBorrowing(session=session)
    result = await app_service.execute(prestamo_id, user_id, request_data)

    if isinstance(result, dict) and result.get("error"):
        status_code = (
            status.HTTP_404_NOT_FOUND
            if result["error"] == "NOT_FOUND"
            else status.HTTP_400_BAD_REQUEST
        )
        return Response(
            data=None,
            message="Error al procesar la devolución",
            status_code=status_code,
            details={"error": result["message"]},
        ).to_dict()

    data_body: Any = result.get("data", {})
    mensaje: str = str(data_body.get("mensaje", ""))
    return Response(
        data=data_body, message=mensaje, status_code=status.HTTP_200_OK
    ).to_dict()


@router.post("/novelty/{novedad_id}/resolve", status_code=status.HTTP_200_OK)
async def resolve_chess_novelty(
    session: SessionDep, novedad_id: int, request_data: ResolveChessNoveltyRequest
):
    app_service = ResolveChessNovelty(session=session)
    result = await app_service.execute(novedad_id, request_data)

    if isinstance(result, dict) and result.get("error"):
        status_code = (
            status.HTTP_404_NOT_FOUND
            if result["error"] == "NOT_FOUND"
            else status.HTTP_400_BAD_REQUEST
        )
        return Response(
            data=None,
            message="Error al resolver la novedad",
            status_code=status_code,
            details={"error": result["message"]},
        ).to_dict()

    data_body: Any = result.get("data", {})
    mensaje: str = str(data_body.get("mensaje", ""))
    return Response(
        data=data_body,
        message=mensaje,
        status_code=status.HTTP_200_OK,
    ).to_dict()


@router.post("/borrow/{prestamo_id}/resolve-novelty", status_code=status.HTTP_200_OK)
async def resolve_borrow_novelty(
    session: SessionDep, prestamo_id: int, request_data: ResolveBorrowNoveltyRequest
):
    app_service = ResolveBorrowNovelty(session=session)
    result = await app_service.execute(prestamo_id, request_data)

    if isinstance(result, dict) and result.get("error"):
        status_code = (
            status.HTTP_404_NOT_FOUND
            if result["error"] == "NOT_FOUND"
            else status.HTTP_400_BAD_REQUEST
        )
        return Response(
            data=None,
            message="Error al resolver la novedad",
            status_code=status_code,
            details={"error": result["message"]},
        ).to_dict()

    data_body: Any = result.get("data", {})
    mensaje: str = str(data_body.get("mensaje", ""))
    return Response(
        data=data_body,
        message=mensaje,
        status_code=status.HTTP_200_OK,
    ).to_dict()


@router.get("/clearance/{estudiante_id}", status_code=status.HTTP_200_OK)
async def get_chess_clearance(session: SessionDep, estudiante_id: int):
    app_service = GetChessClearance(session=session)
    result = await app_service.execute(estudiante_id)
    mensaje: str = str(result.get("message", ""))
    return Response(
        data={"paz_y_salvo": result.get("paz_y_salvo")},
        message=mensaje,
        status_code=status.HTTP_200_OK,
    ).to_dict()


@router.get("/items", status_code=status.HTTP_200_OK)
async def get_chess_items(
    session: SessionDep,
    filter_pagination_query: Annotated[FilterPaginationInventory, Query()],
):
    filter_pagination_query.item_type = "ajedrez"
    inventory_app = GetItemsInventory(session=session)
    total, data = await inventory_app.execute(filter_pagination=filter_pagination_query)

    return (
        Response(
            data=data,
            message="Inventario de ajedrez obtenido exitosamente",
            status_code=status.HTTP_200_OK,
        )
        .filterPagination(
            page=filter_pagination_query.page,
            limit=filter_pagination_query.limit,
            total=total,
        )
        .to_dict()
    )


@router.get("/borrowings", status_code=status.HTTP_200_OK)
async def get_chess_borrowings(
    session: SessionDep,
    filter_pagination_query: Annotated[FilterPaginationBorrowings, Query()],
):
    from app.modules.inventory.infrastructure.repository import InventoryRepository

    filter_pagination_query.item_type = "ajedrez"
    borrowings_app = GetBorrowings(session=session)
    total, data = await borrowings_app.execute(
        filter_pagination=filter_pagination_query
    )

    inventory_repo = InventoryRepository(session=session)
    enriched_data = []
    for borrow in data:
        borrow_dict = borrow.model_dump()
        item = await inventory_repo.get_item_by_id(borrow.inventario_id)
        piezas_totales = 32
        if item and item.observacion and item.observacion.startswith("[PIEZAS:"):
            try:
                parts = item.observacion.split("]", 1)
                num_part = parts[0].replace("[PIEZAS:", "").strip()
                piezas_totales = int(num_part)
            except (ValueError, IndexError):
                pass
        borrow_dict["piezas_totales"] = piezas_totales
        enriched_data.append(borrow_dict)

    return (
        Response(
            data=enriched_data,
            message="Préstamos de ajedrez obtenidos exitosamente",
            status_code=status.HTTP_200_OK,
        )
        .filterPagination(
            page=filter_pagination_query.page,
            limit=filter_pagination_query.limit,
            total=total,
        )
        .to_dict()
    )


@router.post("/items", status_code=status.HTTP_201_CREATED)
async def create_chess_item(session: SessionDep, item_data: CreateChessItemRequest):
    app_service = CreateChessItem(session=session)
    result = await app_service.execute(item_data)

    if isinstance(result, dict):
        error = result.get("error")
        status_code = (
            status.HTTP_404_NOT_FOUND
            if error == "NOT_FOUND"
            else status.HTTP_400_BAD_REQUEST
        )
        return Response(
            data=None,
            message="Error al crear el artículo de ajedrez",
            status_code=status_code,
            details={"error": result.get("message", "")},
        ).to_dict()

    if result is None:
        return Response(
            data=None,
            message="Error al crear el artículo de ajedrez",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ).to_dict()

    piezas_totales = 32
    if result.observacion and result.observacion.startswith("[PIEZAS:"):
        try:
            parts = result.observacion.split("]", 1)
            num_part = parts[0].replace("[PIEZAS:", "").strip()
            piezas_totales = int(num_part)
        except (ValueError, IndexError):
            pass

    return Response(
        data={
            "id": result.id,
            "nombre": result.nombre,
            "cantidad_total": result.cantidad_total,
            "piezas_totales": piezas_totales,
        },
        message="Artículo de ajedrez creado exitosamente",
        status_code=status.HTTP_201_CREATED,
    ).to_dict()
