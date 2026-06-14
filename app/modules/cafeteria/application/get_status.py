from app.core.db import SessionDep
from app.modules.cafeteria.domain.service import CafeteriaService
from app.modules.cafeteria.infrastructure.enrollment_adapter import (
    CafeteriaEnrollmentAdapter,
)
from app.modules.cafeteria.infrastructure.repository import CafeteriaRepository


class GetStatus:
    def __init__(self, session: SessionDep):
        self.service = CafeteriaService(
            repository=CafeteriaRepository(session),
            student_service=CafeteriaEnrollmentAdapter(session),
        )

    async def execute(self, periodo_id: int):
        return await self.service.get_status_list(periodo_id)
