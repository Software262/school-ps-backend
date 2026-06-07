from app.core.db import SessionDep
from app.modules.enrollment.infrastructure.repository import SQLEnrollmentRepository
from app.modules.enrollment.domain.service import StudentService
from app.modules.cafeteria.infrastructure.repository import CafeteriaRepository
from app.modules.cafeteria.domain.service import CafeteriaService


class SearchGeneralStudents:
    def __init__(self, session: SessionDep):
        self.repository = CafeteriaRepository(session)
        enrollment_repo = SQLEnrollmentRepository(session)
        student_service = StudentService(enrollment_repo)
        self.service = CafeteriaService(self.repository, student_service)

    async def execute(self, query: str | None = None, grado_id: int | None = None):
        return await self.service.search_general_students_flat(query, grado_id)
