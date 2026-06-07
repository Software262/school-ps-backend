from app.core.db import SessionDep
from app.modules.enrollment.infrastructure.repository import SQLEnrollmentRepository
from app.modules.enrollment.domain.service import StudentService
from app.modules.cafeteria.infrastructure.repository import CafeteriaRepository
from app.modules.cafeteria.domain.service import CafeteriaService


class UpdateStatus:
    def __init__(self, session: SessionDep):
        self.repository = CafeteriaRepository(session)
        enrollment_repo = SQLEnrollmentRepository(session)
        student_service = StudentService(enrollment_repo)
        self.service = CafeteriaService(self.repository, student_service)

    async def execute(self, registro_ids: list[int], usuario_id: int):
        return await self.service.clear_debts_bulk(registro_ids, usuario_id)
