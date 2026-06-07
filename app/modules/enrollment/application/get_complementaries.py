from app.core.db import SessionDep
from app.modules.enrollment.domain.entities import ComplementaryConcept
from app.modules.enrollment.domain.service import EnrollmentService
from app.modules.enrollment.infrastructure.repository import (
    SQLEnrollmentRepository,
)


class GetComplementaries:
    """Caso de uso: obtener todos los conceptos complementarios."""

    def __init__(self, session: SessionDep) -> None:
        repository = SQLEnrollmentRepository(session)
        self._service = EnrollmentService(repository)

    def execute(self, year: int | None = None) -> list[ComplementaryConcept]:
        return self._service.get_all_complementaries(year=year)
