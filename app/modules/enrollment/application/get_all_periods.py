from app.core.db import SessionDep
from app.modules.enrollment.schemas.response import PeriodResponse
from app.modules.enrollment.domain.service import StudentService
from app.modules.enrollment.infrastructure.repository import SQLEnrollmentRepository


class GetAllPeriods:
    """Caso de uso: listar todos los periodos académicos disponibles."""

    def __init__(self, session: SessionDep) -> None:
        repository = SQLEnrollmentRepository(session)
        self.service = StudentService(repository)

    def execute(self) -> list[PeriodResponse]:
        return self.service.get_all_periods()
