from app.modules.tuition.domain.service import TuitionService
from app.modules.tuition.domain.entities import TuitionInstallment
from app.modules.tuition.schemas.request import PaymentCreateRequest


class RegisterTuitionPaymentUseCase:
    def __init__(self, service: TuitionService):
        self.service = service

    def execute(self, request: PaymentCreateRequest) -> TuitionInstallment:
        return self.service.register_payment(request)
