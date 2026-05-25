from app.core.db import SessionDep
from app.modules.enrollment.domain.service import EnrollmentService
from app.modules.enrollment.infrastructure.repository import (
    SQLEnrollmentRepository,
)
from app.modules.enrollment.schemas.request import ModifyEnrollmentRequest


class ModifyEnrollment:
    """Caso de uso: Modificar los valores de una matrícula en tiempo real."""

    def __init__(self, session: SessionDep) -> None:
        repository = SQLEnrollmentRepository(session)
        self._service = EnrollmentService(repository)

    def execute(self, matricula_id: int, request: ModifyEnrollmentRequest) -> dict:
        return self._service.modify_enrollment(matricula_id, request)
