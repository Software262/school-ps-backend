from app.core.db import SessionDep
from app.modules.enrollment.schemas.response import StudentGeneralResponse
from app.modules.enrollment.domain.service import StudentService
from app.modules.enrollment.infrastructure.repository import SQLEnrollmentRepository


class GetStudentsBulk:
    """Caso de uso: obtener información resumida de un lote de estudiantes."""

    def __init__(self, session: SessionDep) -> None:
        repository = SQLEnrollmentRepository(session)
        self.service = StudentService(repository)

    def execute(self, student_ids: list[int]) -> list[StudentGeneralResponse]:
        return self.service.get_students_bulk(student_ids)
