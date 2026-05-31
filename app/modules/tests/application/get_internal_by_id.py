from app.modules.tests.infrastructure.repository import InternalTestRepository
from app.modules.tests.domain.service import InternalTestService


class GetInternalTestById:
    def __init__(self, session):
        self.repository = InternalTestRepository(session=session)
        self.service = InternalTestService(repository=self.repository)

    async def execute(self, test_id: int):
        return await self.service.get_test_by_id(test_id)
