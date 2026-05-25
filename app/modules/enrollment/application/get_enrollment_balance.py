from app.core.db import SessionDep
from app.modules.enrollment.domain.entities import EnrollmentBalance
from app.modules.enrollment.domain.service import EnrollmentService
from app.modules.enrollment.infrastructure.repository import (
    SQLEnrollmentRepository,
)


class GetEnrollmentBalance:
    """Caso de uso: obtener el balance de matrícula de un estudiante."""

    def __init__(self, session: SessionDep) -> None:
        repository = SQLEnrollmentRepository(session)
        self.service = EnrollmentService(repository)

    def execute(self, student_id: int, year: int) -> EnrollmentBalance:
        return self.service.get_balance(student_id, year)
