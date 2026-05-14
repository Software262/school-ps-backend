from app.modules.inventory.api.domain.repositories import InventoryRepository



class InventoryService:
    
    def __init__(self, repository: InventoryRepository):
        self.repository = repository

    async def get_inventory(self):
        # Implement logic to process inventory data if needed
        return await self.repository.get_inventory()