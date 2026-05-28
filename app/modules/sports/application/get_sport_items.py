from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.sports.domain.service import SportsService
from app.shared.schemas.filter_pagination_request import FilterPagination


class GetSportItems:
    def __init__(self, session):
        self.repository = InventoryRepository(session=session)
        self.service = SportsService(repository=self.repository)

    async def execute(self, filter_pagination: FilterPagination):
        return await self.service.get_sport_items(filter_pagination)
