from app.core.db import SessionDep
from app.modules.tuition.infrastructure.repositories import SQLModelTuitionRepository
from app.modules.tuition.domain.service import TuitionService
from app.modules.tuition.domain.entities import TuitionInstallment
from app.modules.tuition.schemas.request import PaymentCreateRequest


class RegisterTuitionPaymentUseCase:
    def __init__(self, session: SessionDep):
        repo = SQLModelTuitionRepository(session)
        self.service = TuitionService(repo)

    def execute(self, request: PaymentCreateRequest) -> TuitionInstallment:
        return self.service.register_payment(request)
