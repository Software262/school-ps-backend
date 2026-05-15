from app.modules.inventory.domain.repositories import InventoryRepository
from app.modules.inventory.schemas.request import CreateItemRequest

class InventoryService:
    def __init__(self, repository: InventoryRepository):
        self.repository = repository

    async def get_inventory(self):
        return await self.repository.get_inventory()

    async def create_item(self, item_data: CreateItemRequest):
        return await self.repository.create_item(item_data)
    
