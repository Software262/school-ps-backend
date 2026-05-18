from app.core.db import SessionDep
from app.modules.classroom.domain.repositories import PupitreRepository
from app.modules.classroom.domain.service import PupitreService
from app.modules.classroom.schemas.request import PupitreInSchema


class UpdatePupitreState:
    def __init__(self, session: SessionDep):
        self.repository = PupitreRepository(session=session)
        self.service = PupitreService(repositorio=self.repository)

    async def execute(self, estudiante_id: int, request: PupitreInSchema):
        return await self.service.actualizar_estado_estudiante(
            estudiante_id=estudiante_id,
            nuevo_estado=request.estado_pupitre,
            observacion=request.observacion
        )