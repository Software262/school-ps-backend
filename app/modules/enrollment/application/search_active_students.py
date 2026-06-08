from app.core.db import SessionDep
from app.modules.enrollment.schemas.response import StudentGeneralResponse
from app.modules.enrollment.domain.service import StudentService
from app.modules.enrollment.infrastructure.repository import SQLEnrollmentRepository


class SearchActiveStudents:
    """Caso de uso: buscar estudiantes activos."""

    def __init__(self, session: SessionDep) -> None:
        repository = SQLEnrollmentRepository(session)
        self.service = StudentService(repository)

    def execute(
        self,
        query: str | None = None,
        grado_id: int | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[StudentGeneralResponse]:
        return self.service.search_active_students(
            query=query, grado_id=grado_id, limit=limit, offset=offset
        )
