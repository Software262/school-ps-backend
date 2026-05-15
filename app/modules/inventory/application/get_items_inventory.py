from app.modules.inventory.domain.repositories import InventoryRepository
from app.modules.inventory.domain.service import InventoryService


class GetItemsInventory:
    def __init__(self, session):
        self.repository = InventoryRepository(session=session)
        self.service = InventoryService(repository=self.repository)

    async def execute(self):
        return await self.service.get_inventory()
