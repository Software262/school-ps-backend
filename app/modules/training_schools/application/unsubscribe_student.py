from app.modules.training_schools.domain.service import TrainingSchoolsService
from app.modules.training_schools.infrastructure.repository import TrainingSchoolsRepository
from app.modules.training_schools.schemas.request import UnsubscribeRequest


class UnsubscribeStudent:
    def __init__(self, session):
        self.repository = TrainingSchoolsRepository(session=session)
        self.service = TrainingSchoolsService(repository=self.repository)

    async def execute(self, student_id: int, complementario_id: int, mes: str, data: UnsubscribeRequest):
        return await self.service.unsubscribe_student(
            student_id=student_id,
            complementario_id=complementario_id,
            mes=mes,
            data=data
        )
