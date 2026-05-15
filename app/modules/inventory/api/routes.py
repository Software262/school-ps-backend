from fastapi import APIRouter

from app.core.db import SessionDep
from app.modules.inventory.application.create_item_inventory import CreateItemInventory
from app.modules.inventory.application.get_items_inventory import GetItemsInventory
from app.modules.inventory.schemas.request import CreateItemRequest

router = APIRouter()


@router.get("/items")
async def get_inventory(session: SessionDep):
    inventory_app = GetItemsInventory(session=session)
    return await inventory_app.execute()


@router.post("/items")
async def create_item(session: SessionDep, create_item_request: CreateItemRequest):
    create_item_app = CreateItemInventory(session=session)
    return await create_item_app.execute(create_item_request)
