from app.modules.sports.domain.service import SportsService
from app.modules.sports.infrastructure.repository import SportsRepositoryImpl
from app.modules.sports.schemas.request import CreateSportBorrowRequest


class CreateSportBorrow:
    def __init__(self, session):
        self.repository = SportsRepositoryImpl(session=session)
        self.service = SportsService(repository=self.repository)

    async def execute(self, borrow_data: CreateSportBorrowRequest):
        return await self.service.create_sport_borrow(borrow_data)
