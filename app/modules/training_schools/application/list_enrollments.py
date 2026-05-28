from app.modules.training_schools.domain.service import TrainingSchoolsService
from app.modules.training_schools.infrastructure.repository import (
    TrainingSchoolsRepository,
)


class ListEnrollments:
    def __init__(self, session):
        self.repository = TrainingSchoolsRepository(session=session)
        self.service = TrainingSchoolsService(repository=self.repository)

    async def execute(
        self,
        student_id: int | None = None,
        complementario_id: int | None = None,
        mes: str | None = None,
        activo: bool | None = None,
        estado_escuela: bool | None = None,
    ):
        enrollments = await self.service.list_enrollments(
            student_id=student_id,
            complementario_id=complementario_id,
            mes=mes,
            activo=activo,
            estado_escuela=estado_escuela,
        )
        return [
            await self.service.build_enrollment_response(enrollment)
            for enrollment in enrollments
        ]
