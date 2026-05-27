from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.sports.domain.service import SportsService
from app.shared.schemas.filter_pagination import FilterPaginationBorrowings


class GetSportBorrowings:
    def __init__(self, session):
        self.repository = InventoryRepository(session=session)
        self.service = SportsService(repository=self.repository)

    async def execute(self, filter_pagination: FilterPaginationBorrowings):
        return await self.service.get_sport_borrowings(filter_pagination)
