from app.core.db import SessionDep
from app.modules.training_schools.domain.service import TrainingSchoolService
from app.modules.training_schools.infrastructure.enrollment_adapter import (
    EnrollmentAdapter,
)
from app.modules.training_schools.infrastructure.repository import (
    TrainingSchoolRepository,
)


class RegisterPayment:
    def __init__(self, session: SessionDep) -> None:
        self.service = TrainingSchoolService(
            repository=TrainingSchoolRepository(session=session),
            enrollment=EnrollmentAdapter(session),
        )

    async def execute(self, enrollment_id: int, monto: int, usuario_id: int):
        return await self.service.register_payment(enrollment_id, monto, usuario_id)
