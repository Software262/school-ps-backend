from fastapi import APIRouter

from app.core.db import SessionDep
from app.modules.inventory.application.create_item_inventory import CreateItemInventory
from app.modules.inventory.application.get_items_inventory import GetItemsInventory
from app.modules.inventory.schemas.request import (
    CreateItemRequest,
    CreateTypeInventoryRequest,
)
from app.modules.inventory.application.create_type_inventory import CreateTypeInventory


router = APIRouter()


@router.get("/items")
async def get_inventory(session: SessionDep):
    inventory_app = GetItemsInventory(session=session)
    return await inventory_app.execute()


@router.post("/items")
async def create_item(session: SessionDep, create_item_request: CreateItemRequest):
    create_item_app = CreateItemInventory(session=session)
    return await create_item_app.execute(create_item_request)


@router.post("/types")
async def create_type_inventory(
    session: SessionDep, create_type_request: CreateTypeInventoryRequest
):
    create_type_app = CreateTypeInventory(session=session)
    return await create_type_app.execute(create_type_request)
