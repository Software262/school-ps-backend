from app.core.db import SessionDep
from app.modules.inventory.application.create_item_inventory import CreateItemInventory
from app.modules.inventory.infrastructure.enrollment_adapter import (
    InventoryEnrollmentAdapter,
)
from app.modules.sports.domain.service import SportsService
from app.modules.sports.schemas.request import CreateSportItemRequest


class CreateItemDeportes(CreateItemInventory):
    def __init__(self, session: SessionDep):
        super().__init__(session=session)
        self._service = SportsService(
            repository=self.service.repository,
            enrollment=InventoryEnrollmentAdapter(session=session),
        )

    async def _execute(self, item_data: CreateSportItemRequest):
        return await self._service.create_item(item_data=item_data)
