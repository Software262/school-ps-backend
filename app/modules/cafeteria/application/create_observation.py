from app.core.db import SessionDep
from app.modules.enrollment.domain.service import StudentService
from app.modules.cafeteria.infrastructure.repository import CafeteriaRepository
from app.modules.cafeteria.domain.service import CafeteriaService


class CreateObservation:
    def __init__(self, session: SessionDep, student_service: StudentService):
        self.repository = CafeteriaRepository(session)
        self.service = CafeteriaService(self.repository, student_service)

    async def execute(
        self, estudiante_id: int, periodo_id: int, usuario_id: int, obs: str
    ):
        """Creates or updates a debt record for a student."""
        return await self.service.create_manual_block(
            estudiante_id, periodo_id, usuario_id, obs
        )
