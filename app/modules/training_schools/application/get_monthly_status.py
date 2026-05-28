from app.modules.training_schools.domain.service import TrainingSchoolsService
from app.modules.training_schools.infrastructure.repository import (
    TrainingSchoolsRepository,
)


class GetMonthlyStatus:
    def __init__(self, session):
        self.repository = TrainingSchoolsRepository(session=session)
        self.service = TrainingSchoolsService(repository=self.repository)

    async def execute(self, student_id: int, complementario_id: int):
        status_data = await self.service.get_monthly_status(
            student_id, complementario_id
        )
        return {
            **status_data,
            "meses": [
                await self.service.build_enrollment_response(enrollment)
                for enrollment in status_data["meses"]
            ],
        }
