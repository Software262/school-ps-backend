from app.modules.training_schools.domain.service import TrainingSchoolsService
from app.modules.training_schools.infrastructure.repository import (
    TrainingSchoolsRepository,
)
from app.modules.training_schools.schemas.request import CreateProgramRequest


class ListEnrollments:
    def __init__(self, session):
        self.repository = TrainingSchoolsRepository(session=session)
        self.service = TrainingSchoolsService(repository=self.repository)

    async def execute_programs(self):
        return await self.service.list_available_programs()

    async def execute_create_program(self, data: CreateProgramRequest):
        return await self.service.create_program(data)

    async def execute_students(self, query: str):
        return await self.service.search_students(query)

    async def execute_for_student(self, student_id: int):
        return await self.service.list_student_enrollments(student_id)

    async def execute_for_program(self, complementario_id: int):
        return await self.service.list_program_enrollments(complementario_id)

    async def execute(
        self,
        student_id: int | None = None,
        complementario_id: int | None = None,
        mes: str | None = None,
        activo: bool | None = None,
        estado_escuela: bool | None = None,
    ):
        return await self.service.list_enrollments(
            student_id=student_id,
            complementario_id=complementario_id,
            mes=mes,
            activo=activo,
            estado_escuela=estado_escuela,
        )
