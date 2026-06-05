from typing import Annotated

from fastapi import APIRouter, Query, status

from app.core.db import SessionDep
from app.modules.musical_band.application.create_borrowing import (
    CreateInstrumentBorrowMusicalBand,
)
from app.modules.musical_band.application.create_item import CreateItemMusicalBand
from app.modules.musical_band.application.get_borrowings import GetBorrowingsMusicalBand
from app.modules.musical_band.application.get_items import (
    GetItemsMusicalBand,
)
from app.modules.musical_band.application.return_borrowing import (
    ReturnInstrumentBorrowMusicalBand,
)
from app.modules.musical_band.application.update_item import UpdateItem
from app.modules.musical_band.schemas.request import (
    CreateInstrumentBorrowingMusicalBand,
    CreateInstrumentRequest,
    FilterPaginationBorrowingMusicalBand,
    FilterPaginationMusicalBand,
    ReturnInstrumentBorrowingMusicalBand,
    UpdateItemMusicalBand,
)
from app.shared.utils.response import Response

router = APIRouter()


@router.get("/items")
async def get_all_instruments(
    session: SessionDep,
    filter_pagination: Annotated[FilterPaginationMusicalBand, Query()],
):
    get_items = GetItemsMusicalBand(session=session)

    total, data = await get_items.execute(filter_pagination=filter_pagination)

    return (
        Response(
            data=data,
            message="obtenido los articulos de banda exitosamente",
        )
        .filterPagination(
            page=filter_pagination.page, limit=filter_pagination.limit, total=total
        )
        .to_dict()
    )


@router.post("")
async def create_instrument(session: SessionDep, item_data: CreateInstrumentRequest):
    create_item = CreateItemMusicalBand(session=session)

    data = await create_item._execute(item_data=item_data)

    if not data:
        return Response(
            data=None,
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False,
            message="Información invalida",
        ).to_dict()

    return Response(
        data=data,
        message="obtenido los articulos de banda exitosamente",
    ).to_dict()


@router.patch("/{id}")
async def update_instrument(
    session: SessionDep, id: int, item_data: UpdateItemMusicalBand
):
    update_item = UpdateItem(session=session)

    data = await update_item._execute(item_id=id, item_data=item_data)

    if not data:
        return Response(
            data=None,
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False,
            message="invalida información para actualizar",
        )

    return Response(
        data=data,
        status_code=status.HTTP_200_OK,
        message="se actualizo correctamente",
    )


@router.get("/borrowings")
async def get_all_borrowings(
    session: SessionDep,
    filter_pagination: Annotated[FilterPaginationBorrowingMusicalBand, Query()],
):
    get_items = GetBorrowingsMusicalBand(session=session)

    total, data = await get_items.execute(filter_pagination=filter_pagination)

    return (
        Response(
            data=data,
            message="obtenido los articulos de banda exitosamente",
        )
        .filterPagination(
            page=filter_pagination.page, limit=filter_pagination.limit, total=total
        )
        .to_dict()
    )


@router.post("/borrowings")
async def create_borrow_band(
    session: SessionDep, borrow_data: CreateInstrumentBorrowingMusicalBand
):
    create_borrow = CreateInstrumentBorrowMusicalBand(session=session)

    data = await create_borrow._execute(borrow_data=borrow_data)

    if not data:
        return Response(
            data=None,
            success=False,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="fallo el proceso de crear el prestamo",
        )

    return Response(
        data=data,
        message="obtenido los articulos de banda exitosamente",
    ).to_dict()


@router.patch("/borrowings/{borrow_id}")
async def return_borrow_band(
    session: SessionDep,
    borrow_id: int,
    borrow_data: ReturnInstrumentBorrowingMusicalBand,
):
    return_borrow = ReturnInstrumentBorrowMusicalBand(session=session)

    data = await return_borrow._execute(borrow_id=borrow_id, borrow_data=borrow_data)

    if not data:
        return Response(
            data=None,
            success=False,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="fallo el proceso devolver un prestamo",
        )

    return Response(
        data=data,
        message="obtenido los articulos de banda exitosamente",
    ).to_dict()
