from app.core.db import SessionDep
from app.modules.classroom.infrastructure.repository import PupitreRepositoryImpl
from app.modules.classroom.infrastructure.enrollment_adapter import (
    ClassroomEnrollmentAdapter,
)
from app.modules.classroom.domain.service import PupitreService
from app.modules.classroom.schemas.request import PupitreInSchema


class UpdatePupitreState:
    def __init__(self, session: SessionDep):
        self.repository = PupitreRepositoryImpl(session=session)
        self.enrollment_service = ClassroomEnrollmentAdapter(session=session)
        self.service = PupitreService(
            repositorio=self.repository,
            enrollment_service=self.enrollment_service,
        )

    async def execute(self, estudiante_id: int, request: PupitreInSchema):
        return await self.service.update_payment_status(
            estudiante_id=estudiante_id,
            observacion=request.observacion,
        )
