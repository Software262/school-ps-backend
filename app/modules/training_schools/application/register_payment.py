from app.modules.training_schools.domain.service import TrainingSchoolsService
from app.modules.training_schools.infrastructure.repository import TrainingSchoolsRepository
from app.modules.training_schools.schemas.request import RegisterPaymentRequest


class RegisterPayment:
    def __init__(self, session):
        self.repository = TrainingSchoolsRepository(session=session)
        self.service = TrainingSchoolsService(repository=self.repository)

    async def execute(self, data: RegisterPaymentRequest):
        return await self.service.register_payment(data)
