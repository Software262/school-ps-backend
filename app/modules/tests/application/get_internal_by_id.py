from app.modules.tests.domain.service import InternalTestService
from app.modules.tests.infrastructure.enrollment_adapter import EnrollmentAdapter
from app.modules.tests.infrastructure.repository import InternalTestRepository


class GetInternalTestById:
    def __init__(self, session):
        self.service = InternalTestService(
            repository=InternalTestRepository(session=session),
            enrollment=EnrollmentAdapter(session),
        )

    async def execute(self, test_id: int):
        return await self.service.get_test_by_id(test_id)
