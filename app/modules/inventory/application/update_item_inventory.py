from app.modules.inventory.domain.repositories import InventoryRepository
from app.modules.inventory.domain.service import InventoryService
from app.modules.inventory.schemas.request import UpdateItemRequest


class UpdateItemInventory:
    def __init__(self, session):
        self.repository = InventoryRepository(session=session)
        self.service = InventoryService(repository=self.repository)

    async def execute(self, item_id: int, item_data: UpdateItemRequest):
        return await self.service.update_item(item_id, item_data)
