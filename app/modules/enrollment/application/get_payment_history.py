from app.core.db import SessionDep
from app.modules.enrollment.domain.entities import PaymentHistoryItem
from app.modules.enrollment.domain.service import EnrollmentService
from app.modules.enrollment.infrastructure.repository import SQLEnrollmentRepository


class GetPaymentHistory:
    """Caso de uso: obtener el historial de pagos de un estudiante para auditoría."""

    def __init__(self, session: SessionDep) -> None:
        self.service = EnrollmentService(SQLEnrollmentRepository(session))

    def execute(self, student_id: int, year: int) -> list[PaymentHistoryItem]:
        return self.service.get_payment_history(student_id, year)
