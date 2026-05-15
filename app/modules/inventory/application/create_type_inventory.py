from app.modules.inventory.domain.repositories import InventoryRepository
from app.modules.inventory.domain.service import InventoryService
from app.modules.inventory.schemas.request import CreateTypeInventoryRequest


class CreateTypeInventory:
    def __init__(self, session):
        self.repository = InventoryRepository(session=session)
        self.service = InventoryService(repository=self.repository)

    async def execute(self, type_data: CreateTypeInventoryRequest):
        return await self.service.create_type_inventory(type_data)
