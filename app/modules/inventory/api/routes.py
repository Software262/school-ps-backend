from typing import Annotated

from fastapi import APIRouter, Query, status

from app.core.db import SessionDep
from app.modules.inventory.application.create_borrowing_inventory import (
    CreateItemBorrowing,
)
from app.modules.inventory.application.create_item_inventory import CreateItemInventory
from app.modules.inventory.application.create_type_inventory import CreateTypeInventory
from app.modules.inventory.application.get_items_inventory import GetItemsInventory
from app.modules.inventory.application.update_item_inventory import UpdateItemInventory
from app.modules.inventory.schemas.request import (
    CreateBorrowRequest,
    CreateItemRequest,
    CreateTypeInventoryRequest,
    UpdateItemRequest,
)
from app.modules.inventory.schemas.response import (
    CreateItemBorrowingResponse,
    CreateItemInventoryResponse,
    CreateTypeInventoryResponse,
    UpdateItemInventoryResponse,
)
from app.shared.schemas.filter_pagination import FilterPagination
from app.shared.utils.response import Response

router = APIRouter()


@router.get("/items")
async def get_inventory(
    session: SessionDep, filter_pagination_query: Annotated[FilterPagination, Query()]
):
    inventory_app = GetItemsInventory(session=session)
    data = await inventory_app.execute(filter_pagination=filter_pagination_query)

    return (
        Response(
            data=data,
            message="Inventario obtenido exitosamente",
            status_code=status.HTTP_200_OK,
            details={"message": "Inventario obtenido exitosamente"},
        )
        .filterPagination(
            page=filter_pagination_query.page, limit=filter_pagination_query.limit
        )
        .to_dict()
    )


@router.post("/items")
async def create_item(session: SessionDep, create_item_request: CreateItemRequest):
    create_item_app = CreateItemInventory(session=session)
    data = await create_item_app.execute(create_item_request)

    if not data.id:
        return Response(
            data=None,
            message="Error al crear el articulo",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"message": "Error al crear el articulo"},
        ).to_dict()

    if not data.id:
        return Response(
            data=None,
            message="Error al crear el articulo",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"message": "Error al crear el articulo"},
        ).to_dict()

    return Response(
        data=CreateItemInventoryResponse(
            id=data.id,
            nombre=data.nombre,
            cantidad=data.cantidad,
            estado_objeto=data.estado_objeto,
            observacion=data.observacion,
        ),
        message="Articulo creado exitosamente",
        status_code=status.HTTP_201_CREATED,
        details={"message": "Articulo creado exitosamente"},
    ).to_dict()


@router.post("/types")
async def create_type_inventory(
    session: SessionDep, create_type_request: CreateTypeInventoryRequest
):
    create_type_app = CreateTypeInventory(session=session)
    data = await create_type_app.execute(create_type_request)

    if not data.id:
        return Response(
            data=None,
            message="Error al crear el tipo de inventario",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"message": "Error al crear el tipo de inventario"},
        ).to_dict()

    return Response(
        data=CreateTypeInventoryResponse(id=data.id, nombre=data.nombre),
        message="Tipo de inventario creado exitosamente",
        status_code=status.HTTP_201_CREATED,
        details={"message": "Tipo de inventario creado exitosamente"},
    ).to_dict()


@router.put("/items/{item_id}")
async def update_item(
    session: SessionDep, item_id: int, update_item_request: UpdateItemRequest
):
    update_item_app = UpdateItemInventory(session=session)
    data = await update_item_app.execute(item_id, update_item_request)

    if not data:
        return Response(
            data=None,
            message="Error al actualizar el articulo",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"message": "Error al actualizar el articulo"},
        ).to_dict()

    if not data.id:
        return Response(
            data=None,
            message="Error al actualizar el articulo",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"message": "Error al actualizar el articulo"},
        ).to_dict()

    return Response(
        data=UpdateItemInventoryResponse(
            id=data.id,
            nombre=data.nombre,
            cantidad=data.cantidad,
            estado_objeto=data.estado_objeto,
            observacion=data.observacion,
        ),
        message="Articulo actualizado exitosamente",
        status_code=status.HTTP_200_OK,
        details={"message": "Articulo actualizado exitosamente"},
    ).to_dict()


@router.post("/borrow")
async def create_borrowing(session: SessionDep, borrow_data: CreateBorrowRequest):
    create_borrow_app = CreateItemBorrowing(session=session)

    data = await create_borrow_app.execute(borrow_data)

    if not data:
        return Response(
            data=None,
            message="Error al crear el prestamo",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"message": "Error al crear el prestamo"},
        ).to_dict()

    if not data.id:
        return Response(
            data=None,
            message="Error al crear el prestamo",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"message": "Error al crear el prestamo"},
        ).to_dict()

    return Response(
        data=CreateItemBorrowingResponse(
            id=data.id,
            inventario_id=data.inventario_id,
            estudiante_id=data.estudiante_id,
            cantidad=data.cantidad,
            observacion=data.observacion,
        ),
        message="Prestamo creado exitosamente",
        status_code=status.HTTP_201_CREATED,
        details={"message": "Prestamo creado exitosamente"},
    ).to_dict()
