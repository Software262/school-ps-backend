from app.modules.training_schools.domain.service import TrainingSchoolsService
from app.modules.training_schools.infrastructure.repository import (
    TrainingSchoolsRepository,
)
from app.modules.training_schools.schemas.request import CreateProgramRequest


class CreateProgram:
    def __init__(self, session):
        self.repository = TrainingSchoolsRepository(session=session)
        self.service = TrainingSchoolsService(repository=self.repository)

    async def execute(self, data: CreateProgramRequest):
        program = await self.service.create_program(data)
        if not program:
            return None
        return await self.service.build_program_response(program)
