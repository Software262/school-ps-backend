from typing import Annotated, Literal

from fastapi import APIRouter, File, Query, UploadFile, status

from app.core.db import SessionDep
from app.modules.inventory.application.create_borrowing_inventory import (
    CreateItemBorrowing,
)
from app.modules.inventory.application.create_item_inventory import CreateItemInventory
from app.modules.inventory.application.create_items_inventory_from_file import (
    CreateItemsInventoryFromFile,
)
from app.modules.inventory.application.create_type_inventory import CreateTypeInventory
from app.modules.inventory.application.edit_single_item import EditSingleItem
from app.modules.inventory.application.get_borrowings import GetBorrowings
from app.modules.inventory.application.get_items_inventory import GetItemsInventory
from app.modules.inventory.application.get_statics import GetStatsInventory
from app.modules.inventory.application.get_type_by_name import GetTypeByName
from app.modules.inventory.application.get_types_inventory import GetTypesInventory
from app.modules.inventory.application.return_borrowing import ReturnBorrowing
from app.modules.inventory.application.update_item_inventory import UpdateItemInventory
from app.modules.inventory.schemas.request import (
    CreateBorrowRequest,
    CreateItemRequest,
    CreateTypeInventoryRequest,
    FilterPaginationBorrowings,
    FilterPaginationInventory,
    FilterPaginationTypesInventory,
    ReturnBorrowRequest,
    UpdateCompleteItemRequest,
    UpdateSingleItemExtenseRequest,
)
from app.modules.inventory.schemas.response import (
    CreateItemBorrowingResponse,
    CreateItemInventoryResponse,
    CreateTypeInventoryResponse,
    GetInventoryStatsResponse,
    ReturnItemBorrowingResponse,
    UpdateItemInventoryResponse,
)
from app.modules.inventory.utils.file import validate_data, validate_file
from app.shared.utils.response import Response

router = APIRouter()


@router.get("/items")
async def get_inventory(
    session: SessionDep,
    filter_pagination_query: Annotated[FilterPaginationInventory, Query()],
):
    inventory_app = GetItemsInventory(session=session)
    total, data = await inventory_app.execute(filter_pagination=filter_pagination_query)

    return (
        Response(
            data=data,
            message="Inventario obtenido exitosamente",
            status_code=status.HTTP_200_OK,
            details={"message": "Inventario obtenido exitosamente"},
        )
        .filterPagination(
            page=filter_pagination_query.page,
            limit=filter_pagination_query.limit,
            total=total,
        )
        .to_dict()
    )


@router.get("/stats")
async def get_stats_inventory(
    session: SessionDep, type_name: Literal["banda", "deporte", "ajedrez"]
):
    stats_app = GetStatsInventory(session=session)
    (
        total_items,
        available_items,
        borrowed_items,
        maintenance_items,
    ) = await stats_app.execute(type_name=type_name)

    return Response(
        data=GetInventoryStatsResponse(
            total_items=total_items,
            total_disponibles=available_items,
            total_prestados=borrowed_items,
            total_mantenimiento=maintenance_items,
        ).model_dump(),
        message="Estadísticas obtenidas exitosamente",
        status_code=status.HTTP_200_OK,
        details={"message": "Estadísticas obtenidas exitosamente"},
    ).to_dict()


@router.post("/items")
async def create_item(session: SessionDep, create_item_request: CreateItemRequest):
    create_item_app = CreateItemInventory(session=session)
    data = await create_item_app.execute(create_item_request)

    if not data:
        return Response(
            data=None,
            message="Error al crear el articulo",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=False,
            details={"message": "Error al crear el articulo"},
        ).to_dict()

    if not data.id:
        return Response(
            data=None,
            message="Error al crear el articulo",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=False,
            details={"message": "Error al crear el articulo"},
        ).to_dict()

    if not data.id:
        return Response(
            data=None,
            message="Error al crear el articulo",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=False,
            details={"message": "Error al crear el articulo"},
        ).to_dict()

    return Response(
        data=CreateItemInventoryResponse(
            id=data.id,
            nombre=data.nombre,
            cantidad_total=data.cantidad_total,
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
            success=False,
            details={"message": "Error al crear el tipo de inventario"},
        ).to_dict()

    return Response(
        data=CreateTypeInventoryResponse(id=data.id, nombre=data.nombre),
        message="Tipo de inventario creado exitosamente",
        status_code=status.HTTP_201_CREATED,
        details={"message": "Tipo de inventario creado exitosamente"},
    ).to_dict()


@router.get("/types")
async def get_types_inventory(
    session: SessionDep,
    filter_pagination_query: Annotated[FilterPaginationTypesInventory, Query()],
):
    inventory_app = GetTypesInventory(session=session)
    total, data = await inventory_app.execute(filter_pagination=filter_pagination_query)

    return (
        Response(
            data=data,
            message="tipos de inventario obtenido exitosamente",
            status_code=status.HTTP_200_OK,
            details={"message": "tipos de inventario obtenido exitosamente"},
        )
        .filterPagination(
            page=filter_pagination_query.page,
            limit=filter_pagination_query.limit,
            total=total,
        )
        .to_dict()
    )


@router.get("/types/{name}")
async def get_types_by_name(
    session: SessionDep, name: Literal["banda", "ajedrez", "deporte"]
):
    inventory_app = GetTypeByName(session=session)
    data = await inventory_app.execute(name=name)

    if not data:
        return Response(
            data=data,
            message="tipo de inventario no existente",
            success=False,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"message": "tipo de inventario no existente"},
        ).to_dict()

    return Response(
        data=data,
        message="tipo de inventario obtenido exitosamente",
        status_code=status.HTTP_200_OK,
        details={"message": "tipo de inventario obtenido exitosamente"},
    ).to_dict()


@router.put("/items/{item_id}")
async def update_item(
    session: SessionDep, item_id: int, update_item_request: UpdateCompleteItemRequest
):
    update_item_app = UpdateItemInventory(session=session)
    data = await update_item_app.execute(item_id, update_item_request)

    if not data:
        return Response(
            data=None,
            message="Error al actualizar el articulo",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=False,
            details={"message": "Error al actualizar el articulo"},
        ).to_dict()

    if not data.id:
        return Response(
            data=None,
            message="Error al actualizar el articulo",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=False,
            details={"message": "Error al actualizar el articulo"},
        ).to_dict()

    return Response(
        data=UpdateItemInventoryResponse(
            id=data.id,
            nombre=data.nombre,
            cantidad_total=data.cantidad_total,
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
            success=False,
            details={"message": "Error al crear el prestamo"},
        ).to_dict()

    if not data.id:
        return Response(
            data=None,
            message="Error al crear el prestamo",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=False,
            details={"message": "Error al crear el prestamo"},
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
        message="Prestamo creado exitosamente",
        status_code=status.HTTP_201_CREATED,
        details={"message": "Prestamo creado exitosamente"},
    ).to_dict()


@router.patch("/borrow/{borrow_id}")
async def return_borrowing(
    session: SessionDep, borrow_id: int, return_borrow_request: ReturnBorrowRequest
):
    return_borrow_app = ReturnBorrowing(session=session)

    data = await return_borrow_app.execute(borrow_id, return_borrow_request)

    if not data:
        return Response(
            data=None,
            message="Error al devolver el prestamo",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=False,
            details={"message": "Error al devolver el prestamo"},
        ).to_dict()

    if not data.id:
        return Response(
            data=None,
            message="Error al devolver el prestamo",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=False,
            details={"message": "Error al devolver el prestamo"},
        ).to_dict()

    if not data.observacion:
        return Response(
            data=None,
            message="Error al devolver el prestamo",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=False,
            details={"message": "Error al devolver el prestamo"},
        ).to_dict()

    return Response(
        data=ReturnItemBorrowingResponse(
            id=data.id,
            inventario_id=data.inventario_id,
            estudiante_id=data.estudiante_id,
            cantidad=data.cantidad,
            estado_prestamo=data.estado_prestamo,
            observacion=data.observacion,
        ),
        message="Prestamo devuelto exitosamente",
        status_code=status.HTTP_200_OK,
        details={"message": "Prestamo devuelto exitosamente"},
    ).to_dict()


@router.patch("/items/{item_id}")
async def edit_item(
    session: SessionDep,
    item_id: int,
    update_item_request: UpdateSingleItemExtenseRequest,
):
    edit_item_app = EditSingleItem(session=session)
    data = await edit_item_app.execute(item_id, update_item_request)

    if not data:
        return Response(
            data=None,
            message="Error al editar el articulo",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=False,
            details={"message": "Error al editar el articulo"},
        ).to_dict()

    if not data.id:
        return Response(
            data=None,
            message="Error al editar el articulo",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=False,
            details={"message": "Error al editar el articulo"},
        ).to_dict()

    return Response(
        data=UpdateItemInventoryResponse(
            id=data.id,
            nombre=data.nombre,
            cantidad_total=data.cantidad_total,
            observacion=data.observacion,
        ),
        message="Articulo editado exitosamente",
        status_code=status.HTTP_200_OK,
        details={"message": "Articulo editado exitosamente"},
    ).to_dict()


@router.get("/borrow")
async def get_borrowings(
    session: SessionDep,
    filter_pagination_query: Annotated[FilterPaginationBorrowings, Query()],
):
    get_borrowings_app = GetBorrowings(session=session)
    total, data = await get_borrowings_app.execute(
        filter_pagination=filter_pagination_query
    )

    return (
        Response(
            data=data,
            message="Lista de préstamos obtenida exitosamente",
            status_code=status.HTTP_200_OK,
            details={"message": "Lista de préstamos obtenida exitosamente"},
        )
        .filterPagination(
            page=filter_pagination_query.page,
            limit=filter_pagination_query.limit,
            total=total,
        )
        .to_dict()
    )


@router.post("/items/import")
async def upload_items_file(
    session: SessionDep,
    file: Annotated[UploadFile, File()],
):
    data = await validate_file(file=file)

    if data is None:
        return Response(
            data=None,
            message="Archivo invalido solamente se aceptan csv o excel",
            success=False,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={},
        ).to_dict()

    items_inventory = await validate_data(filename=file.filename, data=data)

    create_items_inventory_from_file = CreateItemsInventoryFromFile(session=session)

    res = await create_items_inventory_from_file.execute(
        items_inventory=items_inventory
    )

    return Response(
        data=res,
        message="Archivo cargado exitosamente",
        status_code=status.HTTP_200_OK,
        details={"message": "Archivo cargado exitosamente"},
    ).to_dict()
