from app.core.db import SessionDep
from app.modules.inventory.application.create_item_inventory import CreateItemInventory
from app.modules.inventory.infrastructure.enrollment_adapter import (
    InventoryEnrollmentAdapter,
)
from app.modules.musical_band.domain.service import MusicalBandService
from app.modules.musical_band.schemas.request import CreateInstrumentRequest


class CreateItemMusicalBand(CreateItemInventory):
    def __init__(self, session: SessionDep):
        super().__init__(session=session)
        self._service = MusicalBandService(
            repository=self.service.repository,
            enrollment=InventoryEnrollmentAdapter(session=session),
        )

    async def _execute(self, item_data: CreateInstrumentRequest):
        return await self._service.create_item(item_data=item_data)
