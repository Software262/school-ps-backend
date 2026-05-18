from app.core.db import SessionDep
from app.modules.classroom.domain.repositories import PupitreRepository
from app.modules.classroom.domain.service import PupitreService
from app.modules.classroom.schemas.request import BulkUpdateRequest


class BulkUpdatePupitreState:
    def __init__(self, session: SessionDep):
        self.repository = PupitreRepository(session=session)
        self.service = PupitreService(repositorio=self.repository)

    async def execute(self, grado_id: int, request: BulkUpdateRequest):
        return await self.service.actualizar_estado_masivo(
            grado_id=grado_id,
            nuevo_estado=request.estado_pupitre,
            observacion=request.observacion
        )