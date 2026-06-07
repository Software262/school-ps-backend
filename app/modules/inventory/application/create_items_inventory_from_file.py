from app.core.db import SessionDep
from app.modules.inventory.domain.service import InventoryService
from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.inventory.infrastructure.enrollment_adapter import (
    InventoryEnrollmentAdapter,
)
from app.modules.inventory.schemas.request import InventoryItemRequest


class CreateItemsInventoryFromFile:
    def __init__(self, session: SessionDep):
        self.service = InventoryService(
            repository=InventoryRepository(session=session),
            enrollment=InventoryEnrollmentAdapter(session=session),
        )

    async def execute(self, items_inventory: list[InventoryItemRequest]):
        return await self.service.create_items_inventory_from_file(
            create_items_data=items_inventory
        )
