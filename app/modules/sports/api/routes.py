from typing import Annotated

from fastapi import APIRouter, Query, status

from app.core.db import SessionDep
from app.modules.inventory.schemas.response import (
    CreateItemBorrowingResponse,
    ReturnItemBorrowingResponse,
    UpdateItemInventoryResponse,
)
from app.modules.sports.application.create_borrowing import CreateBorrowingDeportes
from app.modules.sports.application.create_item import CreateItemDeportes
from app.modules.sports.application.edit_single import EditItemDeportes
from app.modules.sports.application.get_borrowing import GetBorrowingsDeportes
from app.modules.sports.application.get_items import (
    GetItemsDeportes,
)
from app.modules.sports.application.return_borrowing import ReturnBorrowingDeportes
from app.modules.sports.application.update_item import UpdateItemDeportes
from app.modules.sports.schemas.request import (
    CreateSportBorrowRequest,
    CreateSportItemRequest,
    FilterPaginationBorrowingDeportes,
    FilterPaginationDeportes,
    ReturnSportBorrowRequest,
    UpdateItemDeportesComplete,
    UpdateItemDeportesSingle,
)
from app.shared.utils.response import Response

router = APIRouter()


@router.get("/items")
async def get_all_sport_items(
    session: SessionDep,
    filter_pagination: Annotated[FilterPaginationDeportes, Query()],
):
    get_items = GetItemsDeportes(session=session)

    total, data = await get_items.execute(filter_pagination=filter_pagination)

    return (
        Response(
            data=data,
            message="obtenido los articulos de deporte exitosamente",
        )
        .filterPagination(
            page=filter_pagination.page, limit=filter_pagination.limit, total=total
        )
        .to_dict()
    )


@router.post("")
async def create_sport_item(session: SessionDep, item_data: CreateSportItemRequest):
    create_item = CreateItemDeportes(session=session)

    data = await create_item._execute(item_data=item_data)

    if not data:
        return Response(
            data=None,
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Información invalida",
        ).to_dict()

    return Response(
        data=data,
        message="obtenido los articulos de deporte exitosamente",
    ).to_dict()


@router.put("/items/{item_id}")
async def update_sport_item(
    session: SessionDep, item_id: int, item_data: UpdateItemDeportesComplete
):
    update_item = UpdateItemDeportes(session=session)
    data = await update_item.execute(item_id, item_data)

    if not data or not data.id:
        return Response(
            data=None,
            message="Error al actualizar el articulo deportivo",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ).to_dict()

    return Response(
        data=UpdateItemInventoryResponse(
            id=data.id,
            nombre=data.nombre,
            cantidad_total=data.cantidad_total,
            observacion=data.observacion,
        ),
        message="Articulo deportivo actualizado exitosamente",
        status_code=status.HTTP_200_OK,
    ).to_dict()


@router.patch("/items/{item_id}")
async def edit_sport_item(
    session: SessionDep, item_id: int, item_data: UpdateItemDeportesSingle
):
    edit_item = EditItemDeportes(session=session)
    data = await edit_item.execute(item_id, item_data)

    if not data or not data.id:
        return Response(
            data=None,
            message="Error al editar el articulo deportivo",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ).to_dict()

    return Response(
        data=UpdateItemInventoryResponse(
            id=data.id,
            nombre=data.nombre,
            cantidad_total=data.cantidad_total,
            observacion=data.observacion,
        ),
        message="Articulo deportivo editado exitosamente",
        status_code=status.HTTP_200_OK,
    ).to_dict()


@router.get("/borrow")
async def get_sport_borrowings(
    session: SessionDep,
    filter_pagination: Annotated[FilterPaginationBorrowingDeportes, Query()],
):
    get_borrowings = GetBorrowingsDeportes(session=session)
    total, data = await get_borrowings.execute(filter_pagination=filter_pagination)

    return (
        Response(
            data=data,
            message="Prestamos deportivos obtenidos exitosamente",
            status_code=status.HTTP_200_OK,
        )
        .filterPagination(
            page=filter_pagination.page, limit=filter_pagination.limit, total=total
        )
        .to_dict()
    )


@router.patch("/borrow/{borrow_id}")
async def return_sport_borrowing(
    session: SessionDep, borrow_id: int, return_data: ReturnSportBorrowRequest
):
    return_borrow = ReturnBorrowingDeportes(session=session)
    data = await return_borrow.execute(borrow_id, return_data)

    if not data or not data.id:
        return Response(
            data=None,
            message="Error al devolver el prestamo deportivo",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ).to_dict()

    return Response(
        data=ReturnItemBorrowingResponse(
            id=data.id,
            inventario_id=data.inventario_id,
            estudiante_id=data.estudiante_id,
            cantidad=data.cantidad,
            estado_prestamo=data.estado_prestamo,
            observacion=data.observacion or "",
        ),
        message="Prestamo deportivo devuelto exitosamente",
        status_code=status.HTTP_200_OK,
    ).to_dict()


@router.post("/borrow")
async def create_sport_borrowing(
    session: SessionDep, borrow_data: CreateSportBorrowRequest
):
    create_borrow = CreateBorrowingDeportes(session=session)
    data = await create_borrow.execute(borrow_data)

    if not data or not data.id:
        return Response(
            data=None,
            message="Error al crear el prestamo deportivo",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ).to_dict()

    return Response(
        data=CreateItemBorrowingResponse(
            id=data.id,
            inventario_id=data.inventario_id,
            estudiante_id=data.estudiante_id,
            cantidad=data.cantidad,
            estado_prestamo=data.estado_prestamo,
            observacion=data.observacion,
        ),
        message="Prestamo deportivo creado exitosamente",
        status_code=status.HTTP_201_CREATED,
    ).to_dict()
