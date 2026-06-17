from app.core.db import SessionDep
from app.modules.classroom.infrastructure.repository import PupitreRepositoryImpl
from app.modules.classroom.infrastructure.enrollment_adapter import (
    ClassroomEnrollmentAdapter,
)
from app.modules.classroom.domain.service import PupitreService
from app.modules.classroom.schemas.request import BulkUpdateRequest


class BulkUpdatePupitreState:
    def __init__(self, session: SessionDep):
        self.repository = PupitreRepositoryImpl(session=session)
        self.enrollment_service = ClassroomEnrollmentAdapter(session=session)
        self.service = PupitreService(
            repositorio=self.repository,
            enrollment_service=self.enrollment_service,
        )

    async def execute(self, grado_id: int, request: BulkUpdateRequest):
        return await self.service.bulk_update_desk_states(
            grado_id=grado_id,
            ids_estudiantes=request.estudiante_ids,
        )
