from app.modules.tests.infrastructure.repository import InternalTestRepository
from app.modules.tests.domain.service import InternalTestService
from app.modules.tests.schemas.request import CreateTestDetailRequest


class CreateInternalTest:
    def __init__(self, session):
        self.repository = InternalTestRepository(session=session)
        self.service = InternalTestService(repository=self.repository)

    async def execute(self, test_data: CreateTestDetailRequest):
        return await self.service.create_test(test_data)
