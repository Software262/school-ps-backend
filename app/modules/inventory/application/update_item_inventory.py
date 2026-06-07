from app.modules.inventory.domain.service import InventoryService
from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.inventory.infrastructure.enrollment_adapter import (
    InventoryEnrollmentAdapter,
)
from app.modules.inventory.schemas.request import UpdateCompleteItemRequest


class UpdateItemInventory:
    def __init__(self, session):
        self.service = InventoryService(
            repository=InventoryRepository(session=session),
            enrollment=InventoryEnrollmentAdapter(session=session),
        )

    async def execute(self, item_id: int, item_data: UpdateCompleteItemRequest):
        return await self.service.update_item(item_id, item_data)
