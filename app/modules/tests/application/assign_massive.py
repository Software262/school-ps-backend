from app.core.db import SessionDep
from app.modules.tests.domain.service import InternalTestService
from app.modules.tests.infrastructure.enrollment_adapter import EnrollmentAdapter
from app.modules.tests.infrastructure.repository import InternalTestRepository
from app.modules.tests.schemas.request import MassiveAssignmentRequest


class AssignMassiveTests:
    def __init__(self, session: SessionDep):
        self.service = InternalTestService(
            repository=InternalTestRepository(session),
            enrollment=EnrollmentAdapter(session),
        )

    async def execute(self, request: MassiveAssignmentRequest):
        return await self.service.assign_massive(request)
