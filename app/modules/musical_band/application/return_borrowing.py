from app.core.db import SessionDep
from app.modules.inventory.application.return_borrowing import ReturnBorrowing
from app.modules.musical_band.domain.service import MusicalBandService
from app.modules.musical_band.schemas.request import (
    ReturnInstrumentBorrowingMusicalBand,
)


class ReturnInstrumentBorrowMusicalBand(ReturnBorrowing):
    def __init__(self, session: SessionDep):
        super().__init__(session=session)
        self._service = MusicalBandService(repository=self.repository)

    async def _execute(
        self, borrow_id: int, borrow_data: ReturnInstrumentBorrowingMusicalBand
    ):
        return await self._service.return_borrowing(
            borrow_id=borrow_id, borrow_data=borrow_data
        )
