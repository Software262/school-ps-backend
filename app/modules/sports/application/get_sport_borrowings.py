from app.modules.sports.domain.service import SportsService
from app.modules.sports.infrastructure.repository import SportsRepositoryImpl


class GetSportBorrowings:
    def __init__(self, session):
        self.repository = SportsRepositoryImpl(session=session)
        self.service = SportsService(repository=self.repository)

    async def execute(self, page: int, limit: int, active: bool | None):
        return await self.service.get_sport_borrowings(
            page=page, limit=limit, active=active
        )
