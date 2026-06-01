from app.modules.sports.domain.service import SportsService
from app.modules.sports.infrastructure.repository import SportsRepository
from app.modules.sports.schemas.request import SportItemFileRequest


class CreateSportItemsFromFile:
    def __init__(self, session):
        self.repository = SportsRepository(session=session)
        self.service = SportsService(repository=self.repository)

    async def execute(self, items_data: list[SportItemFileRequest]):
        return await self.service.create_sport_items_from_file(items_data)
