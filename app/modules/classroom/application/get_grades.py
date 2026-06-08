from app.core.db import SessionDep
from app.modules.classroom.domain.service import PupitreService
from app.modules.classroom.infrastructure.enrollment_adapter import (
    ClassroomEnrollmentAdapter,
)
from app.modules.classroom.infrastructure.repository import PupitreRepositoryImpl


class GetGrades:
    def __init__(self, session: SessionDep):
        self.repository = PupitreRepositoryImpl(session=session)
        self.service = PupitreService(repositorio=self.repository)
        self.students_provider = ClassroomEnrollmentAdapter(session=session)

    async def execute(self):
        return self.students_provider.get_all_grades()
