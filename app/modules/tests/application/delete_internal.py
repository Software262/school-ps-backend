from app.core.db import SessionDep
from app.modules.tests.domain.service import InternalTestService
from app.modules.tests.infrastructure.enrollment_adapter import EnrollmentAdapter
from app.modules.tests.infrastructure.repository import InternalTestRepository


class DeleteInternalTest:
    def __init__(self, session: SessionDep):
        self.service = InternalTestService(
            repository=InternalTestRepository(session),
            enrollment=EnrollmentAdapter(session),
        )

    async def execute(self, test_id: int):
        return await self.service.delete_test(test_id)
