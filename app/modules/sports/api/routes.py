from fastapi import APIRouter, Query, status
from typing import Annotated
from app.core.db import SessionDep
from app.modules.inventory.schemas.request import (
    CreateBorrowRequest,
    ReturnBorrowRequest,
    UpdateCompleteItemRequest,
    UpdateSingleItemRequest,
)
from app.modules.sports.application.create_sport_item import CreateSportItem
from app.modules.sports.application.create_sport_borrowing import CreateSportBorrowing
from app.modules.sports.application.edit_sport_item import EditSportItem
from app.modules.sports.application.get_sport_borrowings import GetSportBorrowings
from app.modules.sports.application.get_sport_items import GetSportItems
from app.modules.sports.application.return_sport_borrowings import ReturnSportBorrowing
from app.modules.sports.application.update_sport_item import UpdateSportItem
from app.modules.sports.schemas.request import CreateSportItemRequest
from app.shared.schemas.filter_pagination import (
    FilterPagination,
    FilterPaginationBorrowings,
)
from app.shared.utils.response import Response

router = APIRouter()


@router.get("/items")
async def get_inventory(
    session: SessionDep, filter_pagination_query: Annotated[FilterPagination, Query()]
):
    inventory_app = GetSportItems(session=session)
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


@router.post("/items", status_code=status.HTTP_201_CREATED)
async def create_sport_item(session: SessionDep, request: CreateSportItemRequest):
    app = CreateSportItem(session=session)
    return await app.execute(request)


@router.put("/items/{item_id}", status_code=status.HTTP_200_OK)
async def update_sport_item(
    item_id: int, session: SessionDep, request: UpdateCompleteItemRequest
):
    app = UpdateSportItem(session=session)
    return await app.execute(item_id, request)


@router.patch("/items/{item_id}", status_code=status.HTTP_200_OK)
async def edit_sport_item(
    item_id: int, session: SessionDep, request: UpdateSingleItemRequest
):
    app = EditSportItem(session=session)
    return await app.execute(item_id, request)


# ── Préstamos ──────────────────────────────────────────────────────────────────


@router.post("/borrow", status_code=status.HTTP_201_CREATED)
async def create_sport_borrowing(session: SessionDep, request: CreateBorrowRequest):
    app = CreateSportBorrowing(session=session)
    return await app.execute(request)


@router.get("/borrow", status_code=status.HTTP_200_OK)
async def get_sport_borrowings(
    session: SessionDep,
    filter_pagination: Annotated[FilterPaginationBorrowings, Query()],
):
    app = GetSportBorrowings(session=session)
    return await app.execute(filter_pagination)


@router.patch("/borrow/{borrow_id}", status_code=status.HTTP_200_OK)
async def return_sport_borrowing(
    borrow_id: int, session: SessionDep, request: ReturnBorrowRequest
):
    app = ReturnSportBorrowing(session=session)
    return await app.execute(borrow_id, request)
