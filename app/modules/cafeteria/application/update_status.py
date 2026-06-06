from app.core.db import SessionDep
from app.modules.enrollment.domain.service import StudentService
from app.modules.cafeteria.infrastructure.repository import CafeteriaRepository
from app.modules.cafeteria.domain.service import CafeteriaService


class UpdateStatus:
    def __init__(self, session: SessionDep, student_service: StudentService):
        self.repository = CafeteriaRepository(session)
        self.service = CafeteriaService(self.repository, student_service)

    async def execute(self, registro_ids: list[int], usuario_id: int):
        """Updates multiple records to 'Paz y Salvo' status."""
        return await self.service.clear_debts_bulk(registro_ids, usuario_id)
