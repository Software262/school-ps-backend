from app.core.db import SessionDep
from app.modules.enrollment.schemas.response import GradeResponse
from app.modules.enrollment.domain.service import StudentService
from app.modules.enrollment.infrastructure.repository import SQLEnrollmentRepository


class GetAllGrades:
    """Caso de uso: listar todos los grados académicos disponibles."""

    def __init__(self, session: SessionDep) -> None:
        repository = SQLEnrollmentRepository(session)
        self.service = StudentService(repository)

    def execute(self) -> list[GradeResponse]:
        return self.service.get_all_grades()
