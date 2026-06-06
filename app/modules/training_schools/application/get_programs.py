from app.core.db import SessionDep
from app.modules.training_schools.domain.service import TrainingSchoolService
from app.modules.training_schools.infrastructure.repository import (
    TrainingSchoolRepository,
)


class GetPrograms:
    def __init__(self, session: SessionDep) -> None:
        self.repository = TrainingSchoolRepository(session=session)
        self.service = TrainingSchoolService(repository=self.repository)

    async def execute(self):
        return await self.service.get_programs()
