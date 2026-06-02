from app.core.db import SessionDep
from app.modules.tests.infrastructure.repository import InternalTestRepository
from app.modules.tests.domain.service import InternalTestService


class GetStudentTestStatus:
    def __init__(self, session: SessionDep):
        self.repository = InternalTestRepository(session)
        self.service = InternalTestService(self.repository)

    async def execute(self, student_id: int):
        return await self.service.get_student_test_status(student_id)
