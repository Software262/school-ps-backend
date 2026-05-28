from app.modules.training_schools.domain.service import TrainingSchoolsService
from app.modules.training_schools.infrastructure.repository import (
    TrainingSchoolsRepository,
)
from app.modules.training_schools.schemas.request import RegisterPaymentRequest


class UnmarkPayment:
    def __init__(self, session):
        self.repository = TrainingSchoolsRepository(session=session)
        self.service = TrainingSchoolsService(repository=self.repository)

    async def execute(self, data: RegisterPaymentRequest):
        payment = await self.service.unmark_payment(data)
        if not payment:
            return None
        return await self.service.build_payment_response(payment)
