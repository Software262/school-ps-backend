from app.modules.inventory.domain.service import InventoryService
from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.shared.schemas.filter_pagination import FilterPaginationBorrowings


SPORT_TYPE_NAME = "deporte"


class GetSportBorrowings:
    def __init__(self, session):
        self.repository = InventoryRepository(session=session)
        self.service = InventoryService(repository=self.repository)

    async def execute(self, filter_pagination: FilterPaginationBorrowings):
        filter_pagination.item_type = "deporte"
        return await self.service.get_borrowings(
            filter_pagination=filter_pagination,
            active=filter_pagination.active,
        )
