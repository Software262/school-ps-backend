from typing import Annotated

from fastapi import APIRouter, Query

from app.core.db import SessionDep
from app.modules.musical_band.application.get_items_musical_band import (
    GetItemsMusicalBand,
)
from app.modules.musical_band.schemas.request import FilterPaginationMusicalBand
from app.shared.utils.response import Response

router = APIRouter()


@router.get("/items")
async def get_all_instruments(
    session: SessionDep,
    filter_pagination: Annotated[FilterPaginationMusicalBand, Query()],
):
    get_items_musicalBand = GetItemsMusicalBand(session=session)

    data = await get_items_musicalBand.execute(filter_pagination=filter_pagination)

    return Response(
        data=data,
    )
