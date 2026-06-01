from typing import Annotated

from fastapi import APIRouter, File, Query, UploadFile, status
from fastapi.responses import JSONResponse

from app.core.db import SessionDep
from app.modules.sports.application.create_sport_borrowing import CreateSportBorrow
from app.modules.sports.application.create_sport_item import CreateSportItem
from app.modules.sports.application.create_sport_items_from_file import (
    CreateSportItemsFromFile,
)
from app.modules.sports.application.create_sport_novedad import CreateSportNovedad
from app.modules.sports.application.edit_sport_item import EditSportItem
from app.modules.sports.application.get_sport_borrowings import GetSportBorrowings
from app.modules.sports.application.get_sport_items import GetSportItems
from app.modules.sports.application.get_sport_paz_y_salvo import GetSportPazYSalvo
from app.modules.sports.application.resolve_sport_novedad import ResolveSportNovedad
from app.modules.sports.application.return_sport_borrowings import ReturnSportBorrow
from app.modules.sports.application.update_sport_item import UpdateSportItem
from app.modules.sports.schemas.request import (
    CreateSportBorrowRequest,
    CreateSportItemRequest,
    CreateSportNovedadRequest,
    FilterPaginationSports,
    FilterPaginationSportsBorrowings,
    ResolveSportNovedadRequest,
    ReturnSportBorrowRequest,
    UpdateCompleteSportItemRequest,
    UpdateSportItemRequest,
)
from app.modules.sports.schemas.response import (
    PazYSalvoStatusResponse,
    ReturnSportBorrowResponse,
    SportBorrowResponse,
    SportItemResponse,
    SportNovedadResponse,
)
from app.modules.sports.utils.file import validate_sport_file, validate_sport_file_data
from app.shared.utils.response import Response

router = APIRouter()


# =========================================================
# ITEMS
# =========================================================


@router.get("/items")
async def get_sport_items(
    session: SessionDep,
    filter_pagination_query: Annotated[FilterPaginationSports, Query()],
):
    use_case = GetSportItems(session=session)
    filter_pagination_query.item_type = "deporte"
    data = await use_case.execute(filter_pagination=filter_pagination_query)
    return (
        Response(
            data=data,
            message="Implementos deportivos obtenidos exitosamente",
            status_code=status.HTTP_200_OK,
            details={"message": "Implementos deportivos obtenidos exitosamente"},
        )
        .filterPagination(
            page=filter_pagination_query.page, limit=filter_pagination_query.limit
        )
        .to_dict()
    )


@router.post("/items", status_code=status.HTTP_201_CREATED)
async def create_sport_item(
    session: SessionDep, create_item_request: CreateSportItemRequest
):
    use_case = CreateSportItem(session=session)
    data = await use_case.execute(create_item_request)

    if not data or not data.id:
        return Response(
            data=None,
            message="Error al crear el implemento deportivo",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"message": "Error al crear el implemento deportivo"},
        ).to_dict()

    return Response(
        data=SportItemResponse(
            id=data.id,
            nombre=data.nombre,
            cantidad=data.cantidad,
            estado_objeto=data.estado_objeto,
            observacion=data.observacion,
        ),
        message="Implemento deportivo creado exitosamente",
        status_code=status.HTTP_201_CREATED,
        details={"message": "Implemento deportivo creado exitosamente"},
    ).to_dict()


@router.put("/items/{item_id}")
async def update_sport_item(
    session: SessionDep,
    item_id: int,
    update_item_request: UpdateCompleteSportItemRequest,
):
    use_case = UpdateSportItem(session=session)
    data = await use_case.execute(item_id, update_item_request)

    if data is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": "Implemento no encontrado o no pertenece al módulo de Deportes"
            },
        )

    return Response(
        data=SportItemResponse(
            id=data.id,
            nombre=data.nombre,
            cantidad=data.cantidad,
            estado_objeto=data.estado_objeto,
            observacion=data.observacion,
        ),
        message="Implemento deportivo actualizado exitosamente",
        status_code=status.HTTP_200_OK,
        details={"message": "Implemento deportivo actualizado exitosamente"},
    ).to_dict()


@router.patch("/items/{item_id}")
async def edit_sport_item(
    session: SessionDep,
    item_id: int,
    update_item_request: UpdateSportItemRequest,
):
    use_case = EditSportItem(session=session)
    data = await use_case.execute(item_id, update_item_request)

    if data is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": "Implemento no encontrado o no pertenece al módulo de Deportes"
            },
        )

    return Response(
        data=SportItemResponse(
            id=data.id,
            nombre=data.nombre,
            cantidad=data.cantidad,
            estado_objeto=data.estado_objeto,
            observacion=data.observacion,
        ),
        message="Implemento deportivo editado exitosamente",
        status_code=status.HTTP_200_OK,
        details={"message": "Implemento deportivo editado exitosamente"},
    ).to_dict()


@router.post("/items/import")
async def import_sport_items(
    session: SessionDep,
    file: Annotated[UploadFile, File()],
):
    raw_data = await validate_sport_file(file=file)

    if raw_data is None:
        return Response(
            data=None,
            message="Archivo inválido. Solo se aceptan CSV o Excel (.xls, .xlsx)",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={},
        ).to_dict()

    items_data = await validate_sport_file_data(filename=file.filename, data=raw_data)

    use_case = CreateSportItemsFromFile(session=session)
    result = await use_case.execute(items_data=items_data)

    return Response(
        data=result,
        message="Archivo de implementos deportivos cargado exitosamente",
        status_code=status.HTTP_200_OK,
        details={"message": "Archivo cargado exitosamente"},
    ).to_dict()


# =========================================================
# PRÉSTAMOS
# =========================================================


@router.post("/borrow", status_code=status.HTTP_201_CREATED)
async def create_sport_borrow(
    session: SessionDep, borrow_data: CreateSportBorrowRequest
):
    use_case = CreateSportBorrow(session=session)
    data = await use_case.execute(borrow_data)

    if data is None:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "message": (
                    "No se pudo crear el préstamo. Verifique que el implemento sea deportivo, "
                    "haya stock suficiente y el estudiante no tenga novedades abiertas."
                )
            },
        )

    return Response(
        data=SportBorrowResponse(
            id=data.id,
            inventario_id=data.inventario_id,
            estudiante_id=data.estudiante_id,
            cantidad=data.cantidad,
            estado_prestamo=data.estado_prestamo,
            fecha_salida=data.fecha_salida,
            fecha_devolucion=data.fecha_devolucion,
            observacion=data.observacion,
        ),
        message="Préstamo deportivo creado exitosamente",
        status_code=status.HTTP_201_CREATED,
        details={"message": "Préstamo creado exitosamente"},
    ).to_dict()


@router.get("/borrow")
async def get_sport_borrowings(
    session: SessionDep,
    filter_pagination_query: Annotated[FilterPaginationSportsBorrowings, Query()],
):
    use_case = GetSportBorrowings(session=session)
    filter_pagination_query.item_type = "deporte"
    data = await use_case.execute(filter_pagination=filter_pagination_query)
    return (
        Response(
            data=data,
            message="Préstamos deportivos obtenidos exitosamente",
            status_code=status.HTTP_200_OK,
            details={"message": "Préstamos deportivos obtenidos exitosamente"},
        )
        .filterPagination(
            page=filter_pagination_query.page, limit=filter_pagination_query.limit
        )
        .to_dict()
    )


@router.patch("/borrow/{borrow_id}")
async def return_sport_borrow(
    session: SessionDep,
    borrow_id: int,
    return_borrow_request: ReturnSportBorrowRequest,
):
    use_case = ReturnSportBorrow(session=session)
    data = await use_case.execute(borrow_id, return_borrow_request)

    if data is None:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "message": (
                    "No se pudo registrar la devolución. Verifique que el préstamo exista, "
                    "sea deportivo, esté activo y los datos coincidan."
                )
            },
        )

    return Response(
        data=ReturnSportBorrowResponse(
            id=data.id,
            inventario_id=data.inventario_id,
            estudiante_id=data.estudiante_id,
            cantidad=data.cantidad,
            estado_prestamo=data.estado_prestamo,
            fecha_devolucion=data.fecha_devolucion,
            observacion=data.observacion,  # type: ignore[arg-type]
        ),
        message="Devolución de implemento deportivo registrada exitosamente",
        status_code=status.HTTP_200_OK,
        details={"message": "Devolución registrada exitosamente"},
    ).to_dict()


# =========================================================
# NOVEDADES
# =========================================================


@router.post("/novedades", status_code=status.HTTP_201_CREATED)
async def create_sport_novedad(
    session: SessionDep, novedad_data: CreateSportNovedadRequest
):
    use_case = CreateSportNovedad(session=session)
    data = await use_case.execute(novedad_data)

    if data is None:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "message": (
                    "No se pudo registrar la novedad. Verifique que el préstamo exista, "
                    "sea deportivo y esté activo."
                )
            },
        )

    return Response(
        data=SportNovedadResponse(
            id=data.id,
            prestamo_id=data.prestamo_id,
            descripcion=data.descripcion,
            resuelta=data.resuelta,
        ),
        message="Novedad deportiva registrada exitosamente",
        status_code=status.HTTP_201_CREATED,
        details={"message": "Novedad registrada exitosamente"},
    ).to_dict()


@router.patch("/novedades/{novedad_id}/resolver")
async def resolve_sport_novedad(
    session: SessionDep,
    novedad_id: int,
    resolve_data: ResolveSportNovedadRequest,
):
    use_case = ResolveSportNovedad(session=session)
    data = await use_case.execute(novedad_id, resolve_data)

    if data is None:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "message": "Novedad no encontrada o ya fue resuelta anteriormente."
            },
        )

    return Response(
        data=SportNovedadResponse(
            id=data.id,
            prestamo_id=data.prestamo_id,
            descripcion=data.descripcion,
            resuelta=data.resuelta,
        ),
        message="Novedad deportiva resuelta exitosamente",
        status_code=status.HTTP_200_OK,
        details={"message": "Novedad resuelta exitosamente"},
    ).to_dict()


# =========================================================
# PAZ Y SALVO
# =========================================================


@router.get("/paz-y-salvo/{estudiante_id}")
async def get_sport_paz_y_salvo(session: SessionDep, estudiante_id: int):
    use_case = GetSportPazYSalvo(session=session)
    data = await use_case.execute(estudiante_id)

    return Response(
        data=PazYSalvoStatusResponse(
            estudiante_id=data.estudiante_id,
            tiene_prestamos_activos=data.tiene_prestamos_activos,
            tiene_novedades_abiertas=data.tiene_novedades_abiertas,
            paz_y_salvo=data.paz_y_salvo,
            detalle=data.detalle,
        ),
        message="Estado de paz y salvo deportivo consultado exitosamente",
        status_code=status.HTTP_200_OK,
        details={"message": "Consulta exitosa"},
    ).to_dict()
