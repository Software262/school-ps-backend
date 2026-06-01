from app.core.db import SessionDep
from app.modules.inventory.application.create_borrowing_inventory import (
    CreateItemBorrowing,
)
from app.modules.sports.domain.service import SportsService
from app.modules.sports.schemas.request import CreateSportBorrowRequest


class CreateSportBorrow(CreateItemBorrowing):
    def __init__(self, session: SessionDep):
        super().__init__(session=session)
        self._service = SportsService(repository=self.repository)

    async def _execute(self, borrow_data: CreateSportBorrowRequest):
        return await self._service.create_sport_borrow(borrow_data)
