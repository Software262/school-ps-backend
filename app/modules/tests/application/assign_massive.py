from app.core.db import SessionDep
from app.modules.tests.infrastructure.repository import InternalTestRepository
from app.modules.tests.domain.service import InternalTestService
from app.modules.tests.schemas.request import MassiveAssignmentRequest


class AssignMassiveTests:
    def __init__(self, session: SessionDep):
        self.repository = InternalTestRepository(session)
        self.service = InternalTestService(self.repository)

    async def execute(self, request: MassiveAssignmentRequest):
        return await self.service.assign_massive(request)
