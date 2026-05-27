from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.inventory.schemas.request import UpdateCompleteItemRequest
from app.modules.sports.domain.service import SportsService


class UpdateSportItem:
    def __init__(self, session):
        self.repository = InventoryRepository(session=session)
        self.service = SportsService(repository=self.repository)

    async def execute(self, item_id: int, item_data: UpdateCompleteItemRequest):
        return await self.service.update_sport_item(item_id, item_data)
