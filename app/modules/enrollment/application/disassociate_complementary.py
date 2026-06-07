from app.core.db import SessionDep
from app.modules.enrollment.domain.service import EnrollmentService
from app.modules.enrollment.infrastructure.repository import (
    SQLEnrollmentRepository,
)


class DisassociateComplementary:
    """Caso de uso: desvincular un concepto complementario de la matrícula de un estudiante."""

    def __init__(self, session: SessionDep) -> None:
        repository = SQLEnrollmentRepository(session)
        self._service = EnrollmentService(repository)

    def execute(self, detalle_id: int) -> int:
        return self._service.disassociate_complementary(detalle_id=detalle_id)
