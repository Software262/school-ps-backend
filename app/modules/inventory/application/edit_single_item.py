from app.modules.inventory.domain.service import InventoryService
from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.inventory.schemas.request import UpdateItemRequest


class EditSingleItem:
    def __init__(self, session):
        self.repository = InventoryRepository(session=session)
        self.service = InventoryService(repository=self.repository)

    async def execute(self, item_id: int, item_data: UpdateItemRequest):
        return await self.service.edit_item(item_id, item_data)
