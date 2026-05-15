from app.modules.inventory.domain.repositories import InventoryRepository
from app.modules.inventory.schemas.request import (
    CreateItemRequest,
    CreateTypeInventoryRequest,
)


class InventoryService:
    def __init__(self, repository: InventoryRepository):
        self.repository = repository

    async def get_inventory(self):
        return await self.repository.get_inventory()

    async def create_item(self, item_data: CreateItemRequest):
        return await self.repository.create_item(item_data)

    async def create_type_inventory(self, type_data: CreateTypeInventoryRequest):
        return await self.repository.create_type_inventory(name=type_data.nombre)
