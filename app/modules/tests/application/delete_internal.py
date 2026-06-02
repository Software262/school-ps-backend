from app.core.db import SessionDep
from app.modules.tests.infrastructure.repository import InternalTestRepository
from app.modules.tests.domain.service import InternalTestService


class DeleteInternalTest:
    def __init__(self, session: SessionDep):
        self.repository = InternalTestRepository(session)
        self.service = InternalTestService(self.repository)

    async def execute(self, test_id: int):
        return await self.service.delete_test(test_id)
