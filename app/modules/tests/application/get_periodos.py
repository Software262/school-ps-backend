from app.core.db import SessionDep
from app.modules.tests.infrastructure.repository import InternalTestRepository
from app.modules.tests.domain.service import InternalTestService


class GetPeriodos:
    def __init__(self, session: SessionDep):
        self.repository = InternalTestRepository(session)
        self.service = InternalTestService(self.repository)

    async def execute(self):
        return await self.service.get_all_periodos()
