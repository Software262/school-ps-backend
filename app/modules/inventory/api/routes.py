from fastapi import APIRouter

from app.core.db import SessionDep
from app.modules.inventory.application.get_items_inventory import GetItemsInventory

router = APIRouter()


@router.get("/items")
async def get_inventory(session: SessionDep):
    inventory_app = GetItemsInventory(session=session)
    return await inventory_app.execute()
