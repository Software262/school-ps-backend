from app.core.db import SessionDep
from app.modules.peace_safe.domain.service import PeaceSafeService
from app.modules.peace_safe.infrastructure.repository import PeaceSafeRepository
from app.modules.peace_safe.schemas.response import StatusResponse


class GetStudentStatus:
    def __init__(self, session: SessionDep):
        self.service = PeaceSafeService(PeaceSafeRepository(session))

    async def execute(self, estudiante_id: int) -> StatusResponse | None:
        return self.service.get_student_status(estudiante_id)
