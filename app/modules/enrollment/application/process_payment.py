from app.core.db import SessionDep
from app.modules.enrollment.domain.entities import PaymentResult
from app.modules.enrollment.domain.service import EnrollmentService
from app.modules.enrollment.infrastructure.repository import (
    SQLEnrollmentRepository,
)


class ProcessDirectedPayment:
    """Caso de uso: pago con asignación dirigida."""

    def __init__(self, session: SessionDep) -> None:
        repository = SQLEnrollmentRepository(session)
        self.service = EnrollmentService(repository)

    def execute(
        self,
        matricula_id: int,
        asignaciones: list[tuple[str, int | None, int | None, int]],
        codigo_talonario: str,
        observacion: str | None = None,
    ) -> PaymentResult:
        return self.service.process_directed_payment(
            matricula_id, asignaciones, codigo_talonario, observacion
        )
