from app.modules.inventory.domain.service import InventoryService
from app.modules.inventory.infrastructure.repository import InventoryRepository
from app.modules.inventory.infrastructure.enrollment_adapter import (
    InventoryEnrollmentAdapter,
)
from app.modules.inventory.schemas.request import FilterPaginationTypesInventory


class GetTypesInventory:
    def __init__(self, session):
        self.service = InventoryService(
            repository=InventoryRepository(session=session),
            enrollment=InventoryEnrollmentAdapter(session=session),
        )

    async def execute(self, filter_pagination: FilterPaginationTypesInventory):
        return await self.service.get_types_inventory(
            filter_pagination=filter_pagination
        )
