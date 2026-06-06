from app.core.db import SessionDep
from app.modules.inventory.application.create_borrowing_inventory import (
    CreateItemBorrowing,
)
from app.modules.musical_band.domain.service import MusicalBandService
from app.modules.musical_band.schemas.request import (
    CreateInstrumentBorrowingMusicalBand,
)


class CreateInstrumentBorrowMusicalBand(CreateItemBorrowing):
    def __init__(self, session: SessionDep):
        super().__init__(session=session)
        self._service = MusicalBandService(repository=self.repository)

    async def _execute(self, borrow_data: CreateInstrumentBorrowingMusicalBand):
        return await self._service.create_borrowing(borrow_data=borrow_data)
