from app.core.db import SessionDep
from app.modules.tests.infrastructure.repository import InternalTestRepository
from app.modules.tests.domain.service import InternalTestService
from app.modules.tests.schemas.request import PaymentRequest


class RegisterTestPayment:
    def __init__(self, session: SessionDep):
        self.repository = InternalTestRepository(session)
        self.service = InternalTestService(self.repository)

    async def execute(self, test_id: int, request: PaymentRequest):
        return await self.service.register_test_payment(test_id, request)
