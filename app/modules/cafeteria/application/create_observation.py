from app.core.db import SessionDep
from app.modules.cafeteria.domain.service import CafeteriaService
from app.modules.cafeteria.infrastructure.repository import CafeteriaRepository
from app.modules.enrollment.domain.service import StudentService
from app.modules.enrollment.infrastructure.repository import SQLEnrollmentRepository


class CreateObservation:
    def __init__(self, session: SessionDep):
        self.repository = CafeteriaRepository(session)
        enrollment_repo = SQLEnrollmentRepository(session)
        student_service = StudentService(enrollment_repo)
        self.service = CafeteriaService(self.repository, student_service)

    async def execute(
        self, estudiante_id: int, periodo_id: int, usuario_id: int, obs: str
    ):
        return await self.service.create_manual_block(
            estudiante_id, periodo_id, usuario_id, obs
        )
