from app.core.db import SessionDep
from app.modules.training_schools.domain.service import TrainingSchoolService
from app.modules.training_schools.infrastructure.repository import (
    TrainingSchoolRepository,
)


class GetPazYSalvo:
    def __init__(self, session: SessionDep) -> None:
        self.repository = TrainingSchoolRepository(session=session)
        self.service = TrainingSchoolService(repository=self.repository)

    async def execute(self, estudiante_id: int) -> bool:
        return await self.service.get_student_paz_y_salvo(estudiante_id)
