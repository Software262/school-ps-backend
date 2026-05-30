from app.modules.sports.domain.service import SportsService
from app.modules.sports.infrastructure.repository import SportsRepositoryImpl


class GetSportPazYSalvo:
    def __init__(self, session):
        self.repository = SportsRepositoryImpl(session=session)
        self.service = SportsService(repository=self.repository)

    async def execute(self, estudiante_id: int):
        return await self.service.get_paz_y_salvo_status(estudiante_id)
