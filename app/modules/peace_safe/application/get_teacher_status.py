from sqlmodel import Session

from app.modules.peace_safe.domain.service import PeaceSafeService
from app.modules.peace_safe.infrastructure.repository import PeaceSafeRepository


class GetTeacherStatus:
    def __init__(self, session: Session):
        self.service = PeaceSafeService(PeaceSafeRepository(session))

    async def execute(self, docente_id: int) -> dict | None:
        result = self.service.get_teacher_status(docente_id)
        return result.to_dict() if result else None
