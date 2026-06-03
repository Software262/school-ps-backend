from app.core.db import SessionDep
from app.modules.training_schools.domain.service import TrainingSchoolService
from app.modules.training_schools.infrastructure.repository import (
    TrainingSchoolRepository,
)


class WithdrawStudent:
    def __init__(self, session: SessionDep) -> None:
        self.repository = TrainingSchoolRepository(session=session)
        self.service = TrainingSchoolService(repository=self.repository)

    async def execute(self, enrollment_id: int, motivo: str, usuario_id: int):
        return await self.service.withdraw_student(enrollment_id, motivo, usuario_id)
