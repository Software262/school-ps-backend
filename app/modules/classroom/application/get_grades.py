from app.core.db import SessionDep
from app.modules.classroom.infrastructure.enrollment_adapter import (
    ClassroomEnrollmentAdapter,
)


class GetGrades:
    def __init__(self, session: SessionDep):
        self.students_provider = ClassroomEnrollmentAdapter(session=session)

    async def execute(self):
        return self.students_provider.get_all_grades()
