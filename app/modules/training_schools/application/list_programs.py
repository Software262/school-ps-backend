from app.modules.training_schools.domain.service import TrainingSchoolsService
from app.modules.training_schools.infrastructure.repository import (
    TrainingSchoolsRepository,
)


class ListPrograms:
    def __init__(self, session):
        self.repository = TrainingSchoolsRepository(session=session)
        self.service = TrainingSchoolsService(repository=self.repository)

    async def execute(self):
        programs = await self.service.list_available_programs()
        return [
            await self.service.build_program_response(program) for program in programs
        ]
