from app.modules.inventory.domain.repositories import InventoryRepository
from app.modules.inventory.domain.service import InventoryService
from app.modules.inventory.schemas.request import CreateItemRequest


class CreateItemInventory:
    def __init__(self, session):
        self.repository = InventoryRepository(session=session)
        self.service = InventoryService(repository=self.repository)

    async def execute(self, item_data: CreateItemRequest):
        return await self.service.create_item(item_data)
