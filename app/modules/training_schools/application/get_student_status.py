from app.modules.training_schools.domain.service import TrainingSchoolsService
from app.modules.training_schools.infrastructure.repository import (
    TrainingSchoolsRepository,
)


class GetStudentStatus:
    def __init__(self, session):
        self.repository = TrainingSchoolsRepository(session=session)
        self.service = TrainingSchoolsService(repository=self.repository)

    async def execute(self, student_id: int):
        return await self.service.get_student_status(student_id)

    async def execute_monthly(self, student_id: int, complementario_id: int):
        return await self.service.get_monthly_status(
            student_id=student_id,
            complementario_id=complementario_id,
        )
