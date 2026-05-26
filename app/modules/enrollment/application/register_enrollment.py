from app.core.db import SessionDep
from app.modules.enrollment.domain.entities import EnrollmentCreated
from app.modules.enrollment.domain.service import EnrollmentService
from app.modules.enrollment.infrastructure.repository import (
    SQLEnrollmentRepository,
)


class RegisterEnrollment:
    """Caso de uso: registrar matrícula automáticamente para un estudiante."""

    def __init__(self, session: SessionDep) -> None:
        repository = SQLEnrollmentRepository(session)
        self.service = EnrollmentService(repository)

    def execute(self, student_id: int, period_id: int, year: int) -> EnrollmentCreated:
        return self.service.register_enrollment(student_id, period_id, year)
