from app.core.db import SessionDep
from app.modules.classroom.infrastructure.repository import PupitreRepositoryImpl
from app.modules.classroom.domain.service import PupitreService

class GetPupitresByGrade:
    def __init__(self, session: SessionDep):
        self.repository = PupitreRepositoryImpl(session=session)
        self.service = PupitreService(repositorio=self.repository)

    async def execute(self, grado_id: int):
        return await self.service.obtener_pupitres(grado_id=grado_id)