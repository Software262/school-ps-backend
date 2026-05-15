from fastapi import APIRouter

from app.core.db import SessionDep
from app.modules.inventory.api.domain.repositories import InventoryRepository
from app.modules.inventory.api.domain.service import InventoryService

router = APIRouter()


@router.get("/items")
async def get_inventory(session: SessionDep):
    inventory_service = InventoryService(
        repository=InventoryRepository(session=session)
    )
    return await inventory_service.get_inventory()
