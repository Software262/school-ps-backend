from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.sports.domain.service import SportsService
from app.modules.sports.schemas.request import CreateSportItemRequest


class CreateSportItem:
    def __init__(self, session):
        self.repository = InventoryRepository(session=session)
        self.service = SportsService(repository=self.repository)

    async def execute(self, item_data: CreateSportItemRequest):
        return await self.service.create_sport_item(item_data)
