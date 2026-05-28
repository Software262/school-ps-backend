from app.modules.training_schools.domain.service import TrainingSchoolsService
from app.modules.training_schools.infrastructure.repository import (
    TrainingSchoolsRepository,
)
from app.modules.training_schools.schemas.request import UnsubscribeRequest


class UnsubscribeProgram:
    def __init__(self, session):
        self.repository = TrainingSchoolsRepository(session=session)
        self.service = TrainingSchoolsService(repository=self.repository)

    async def execute(
        self, student_id: int, complementario_id: int, data: UnsubscribeRequest
    ):
        enrollments = await self.service.unsubscribe_student_from_program(
            student_id=student_id,
            complementario_id=complementario_id,
            data=data,
        )
        return [
            await self.service.build_enrollment_response(enrollment)
            for enrollment in enrollments
        ]
