from typing import Annotated

from fastapi import APIRouter, Query, status

from app.core.db import SessionDep
from app.modules.sports.application.create_item import CreateItemDeportes
from app.modules.sports.application.get_borrowings import GetBorrowingsDeportes
from app.modules.sports.application.get_items import (
    GetItemsDeportes,
)
from app.modules.sports.application.update_item import UpdateItem
from app.modules.sports.schemas.request import (
    CreateSportItemRequest,
    FilterPaginationBorrowingDeportes,
    FilterPaginationDeportes,
    UpdateItemDeportes,
)
from app.shared.utils.response import Response

router = APIRouter()


@router.get("/items")
async def get_all_sport_items(
    session: SessionDep,
    filter_pagination: Annotated[FilterPaginationDeportes, Query()],
):
    get_items = GetItemsDeportes(session=session)

    data = await get_items.execute(filter_pagination=filter_pagination)

    return (
        Response(
            data=data,
            message="obtenido los articulos de deporte exitosamente",
        )
        .filterPagination(page=filter_pagination.page, limit=filter_pagination.limit)
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


@router.patch("")
async def update_sport_item(
    session: SessionDep, id: int, item_data: UpdateItemDeportes
):
    update_item = UpdateItem(session=session)

    data = await update_item._execute(item_id=id, item_data=item_data)

    if not data:
        return Response(
            data=None,
            status_code=status.HTTP_400_BAD_REQUEST,
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
    filter_pagination: Annotated[FilterPaginationBorrowingDeportes, Query()],
):
    get_items = GetBorrowingsDeportes(session=session)

    filter_pagination.item_type = "deporte"

    data = await get_items.execute(filter_pagination=filter_pagination)

    return (
        Response(
            data=data,
            message="obtenido los articulos de deporte exitosamente",
        )
        .filterPagination(page=filter_pagination.page, limit=filter_pagination.limit)
        .to_dict()
    )
