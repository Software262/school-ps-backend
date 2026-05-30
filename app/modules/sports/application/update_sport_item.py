from app.modules.sports.domain.service import SportsService
from app.modules.sports.infrastructure.repository import SportsRepositoryImpl
from app.modules.sports.schemas.request import UpdateCompleteSportItemRequest


class UpdateSportItem:
    def __init__(self, session):
        self.repository = SportsRepositoryImpl(session=session)
        self.service = SportsService(repository=self.repository)

    async def execute(self, item_id: int, item_data: UpdateCompleteSportItemRequest):
        return await self.service.update_sport_item_complete(item_id, item_data)
