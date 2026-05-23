from app.modules.training_schools.domain.service import TrainingSchoolsService
from app.modules.training_schools.infrastructure.repository import TrainingSchoolsRepository


class ListEnrollments:
    def __init__(self, session):
        self.repository = TrainingSchoolsRepository(session=session)
        self.service = TrainingSchoolsService(repository=self.repository)

    async def execute_for_student(self, student_id: int):
        return await self.service.list_student_enrollments(student_id)

    async def execute_for_program(self, complementario_id: int):
        return await self.service.list_program_enrollments(complementario_id)
