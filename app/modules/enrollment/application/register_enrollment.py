from app.core.db import SessionDep
from app.modules.enrollment.domain.entities import EnrollmentCreated
from app.modules.enrollment.domain.service import EnrollmentService
from app.modules.enrollment.infrastructure.repository import (
    SQLEnrollmentRepository,
)
from app.modules.tuition.infrastructure.enrollment_adapter import (
    TuitionEnrollmentAdapter,
)


class RegisterEnrollment:
    """Caso de uso: registrar matrícula automáticamente para un estudiante."""

    def __init__(self, session: SessionDep) -> None:
        repository = SQLEnrollmentRepository(session)
        tuition_service = TuitionEnrollmentAdapter(session)
        self.service = EnrollmentService(repository, tuition_service)

    def execute(
        self, student_id: int, period_id: int | None = None, year: int = 2026
    ) -> EnrollmentCreated:
        return self.service.register_enrollment(student_id, period_id, year)
