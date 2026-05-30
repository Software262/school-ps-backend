from app.modules.sports.domain.service import SportsService
from app.modules.sports.infrastructure.repository import SportsRepositoryImpl
from app.modules.sports.schemas.request import ReturnSportBorrowRequest


class ReturnSportBorrow:
    def __init__(self, session):
        self.repository = SportsRepositoryImpl(session=session)
        self.service = SportsService(repository=self.repository)

    async def execute(self, borrow_id: int, borrow_data: ReturnSportBorrowRequest):
        return await self.service.return_sport_borrow(borrow_id, borrow_data)
