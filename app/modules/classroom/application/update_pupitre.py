from app.core.db import SessionDep
from app.modules.classroom.infrastructure.repository import PupitreRepositoryImpl
from app.modules.classroom.domain.service import PupitreService
from app.modules.classroom.schemas.request import PupitreInSchema


class UpdatePupitreState:
    def __init__(self, session: SessionDep):
        self.repository = PupitreRepositoryImpl(session=session)
        self.service = PupitreService(repositorio=self.repository)

    async def execute(self, estudiante_id: int, request: PupitreInSchema):
        return await self.service.update_desk_state(
            estudiante_id=estudiante_id,
            nuevo_estado=request.estado_pupitre,
            observacion=request.observacion,
        )
