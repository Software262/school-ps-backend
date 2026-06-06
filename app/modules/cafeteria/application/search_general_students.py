from app.core.db import SessionDep
from app.modules.enrollment.domain.service import StudentService
from app.modules.cafeteria.infrastructure.repository import CafeteriaRepository
from app.modules.cafeteria.domain.service import CafeteriaService


class SearchGeneralStudents:
    def __init__(self, session: SessionDep, student_service: StudentService):
        self.repository = CafeteriaRepository(session)
        self.service = CafeteriaService(self.repository, student_service)

    async def execute(self, query: str | None = None, grado_id: int | None = None):
        """Searches students across the school using the cross-module service."""
        return await self.service.search_general_students_flat(query, grado_id)
