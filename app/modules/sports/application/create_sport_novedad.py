from app.modules.sports.domain.service import SportsService
from app.modules.sports.infrastructure.repository import SportsRepositoryImpl
from app.modules.sports.schemas.request import CreateSportNovedadRequest


class CreateSportNovedad:
    def __init__(self, session):
        self.repository = SportsRepositoryImpl(session=session)
        self.service = SportsService(repository=self.repository)

    async def execute(self, novedad_data: CreateSportNovedadRequest):
        return await self.service.create_sport_novedad(novedad_data)
