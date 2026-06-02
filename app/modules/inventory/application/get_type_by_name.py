from app.modules.inventory.domain.service import InventoryService
from app.modules.inventory.infrastructure.repository import InventoryRepository


class GetTypeByName:
    def __init__(self, session):
        self.repository = InventoryRepository(session=session)
        self.service = InventoryService(repository=self.repository)

    async def execute(self, name: str):
        return await self.service.get_type_by_name(name=name)
