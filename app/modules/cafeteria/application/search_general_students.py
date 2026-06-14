from app.core.db import SessionDep
from app.modules.cafeteria.domain.service import CafeteriaService
from app.modules.cafeteria.infrastructure.enrollment_adapter import (
    CafeteriaEnrollmentAdapter,
)
from app.modules.cafeteria.infrastructure.repository import CafeteriaRepository


class SearchGeneralStudents:
    def __init__(self, session: SessionDep):
        self.service = CafeteriaService(
            repository=CafeteriaRepository(session),
            student_service=CafeteriaEnrollmentAdapter(session),
        )

    async def execute(self, query: str | None = None, grado_id: int | None = None):
        return await self.service.search_general_students_flat(query, grado_id)
