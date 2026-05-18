from app.modules.inventory.domain.service import InventoryService
from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.shared.schemas.filter_pagination import FilterPagination


class GetItemsInventory:
    def __init__(self, session):
        self.repository = InventoryRepository(session=session)
        self.service = InventoryService(repository=self.repository)

    async def execute(self, filter_pagination: FilterPagination):
        return await self.service.get_inventory(filter_pagination=filter_pagination)
