from typing import Sequence

from app.modules.inventory.domain.service import InventoryService
from app.modules.inventory.infrastructure.models import Prestamo
from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.shared.schemas.filter_pagination import FilterPaginationBorrowings


class GetBorrowings:
    def __init__(self, session):
        self.repository = InventoryRepository(session=session)
        self.service = InventoryService(self.repository)

    async def execute(
        self, filter_pagination: FilterPaginationBorrowings
    ) -> Sequence[Prestamo]:
        return await self.service.get_borrowings(
            filter_pagination=filter_pagination,
            active=filter_pagination.active,
        )
