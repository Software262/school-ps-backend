from typing import Sequence
from app.modules.inventory.infrastructure.models import Prestamo
from app.shared.schemas.filter_pagination import FilterPagination

from app.modules.inventory.infrastructure.repository import InventoryRepository

class GetBorrowings:
    def __init__(self, session):
        self.repository = InventoryRepository(session=session)

    async def execute(self, filter_pagination: FilterPagination, active_only: bool = False) -> Sequence[Prestamo]:
        offset = (filter_pagination.page - 1) * filter_pagination.limit
        
        return await self.repository.get_borrowings_pagination(
            offset=offset, limit=filter_pagination.limit, active_only=active_only
        )