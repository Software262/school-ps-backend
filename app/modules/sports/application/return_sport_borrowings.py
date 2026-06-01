from app.core.db import SessionDep
from app.modules.inventory.application.return_borrowing import ReturnBorrowing
from app.modules.sports.domain.service import SportsService
from app.modules.sports.schemas.request import ReturnSportBorrowRequest


class ReturnSportBorrow(ReturnBorrowing):
    def __init__(self, session: SessionDep):
        super().__init__(session=session)
        self._service = SportsService(repository=self.repository)

    async def _execute(self, borrow_id: int, borrow_data: ReturnSportBorrowRequest):
        return await self._service.return_sport_borrow(borrow_id, borrow_data)
