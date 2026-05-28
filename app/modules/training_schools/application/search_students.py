from app.modules.training_schools.domain.service import TrainingSchoolsService
from app.modules.training_schools.infrastructure.repository import (
    TrainingSchoolsRepository,
)


class SearchStudents:
    def __init__(self, session):
        self.repository = TrainingSchoolsRepository(session=session)
        self.service = TrainingSchoolsService(repository=self.repository)

    async def execute(self, query: str):
        students = await self.service.search_students(query)
        return [
            await self.service.build_student_response(student) for student in students
        ]
