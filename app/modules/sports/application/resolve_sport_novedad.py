from app.modules.sports.domain.service import SportsService
from app.modules.sports.infrastructure.repository import SportsRepository
from app.modules.sports.schemas.request import ResolveSportNovedadRequest


class ResolveSportNovedad:
    def __init__(self, session):
        self.repository = SportsRepository(session=session)
        self.service = SportsService(repository=self.repository)

    async def execute(self, novedad_id: int, resolve_data: ResolveSportNovedadRequest):
        return await self.service.resolve_sport_novedad(novedad_id, resolve_data)
