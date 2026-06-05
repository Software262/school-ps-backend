from app.core.db import SessionDep
from app.modules.enrollment.domain.entities import PaymentReceipt
from app.modules.enrollment.domain.service import EnrollmentService
from app.modules.enrollment.infrastructure.repository import SQLEnrollmentRepository


class GetPaymentReceipt:
    """Caso de uso: obtener los datos completos de un recibo/comprobante de pago."""

    def __init__(self, session: SessionDep) -> None:
        self.service = EnrollmentService(SQLEnrollmentRepository(session))

    def execute(self, pago_id: int) -> PaymentReceipt:
        return self.service.get_payment_receipt(pago_id)
