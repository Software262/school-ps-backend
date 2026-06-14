from app.core.db import SessionDep
from app.modules.cafeteria.domain.service import CafeteriaService
from app.modules.cafeteria.infrastructure.enrollment_adapter import (
    CafeteriaEnrollmentAdapter,
)
from app.modules.cafeteria.infrastructure.repository import CafeteriaRepository


class CreateObservation:
    def __init__(self, session: SessionDep):
        self.service = CafeteriaService(
            repository=CafeteriaRepository(session),
            student_service=CafeteriaEnrollmentAdapter(session),
        )

    async def execute(
        self, estudiante_id: int, periodo_id: int, usuario_id: int, obs: str
    ):
        return await self.service.create_manual_block(
            estudiante_id, periodo_id, usuario_id, obs
        )
