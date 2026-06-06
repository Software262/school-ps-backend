from app.core.db import SessionDep
from app.modules.enrollment.domain.service import StudentService
from app.modules.cafeteria.infrastructure.repository import CafeteriaRepository
from app.modules.cafeteria.domain.service import CafeteriaService


class RemoveBlock:
    def __init__(self, session: SessionDep, student_service: StudentService):
        self.repository = CafeteriaRepository(session)
        self.service = CafeteriaService(self.repository, student_service)

    async def execute(self, registro_ids: list[int], usuario_id: int):
        return await self.service.bulk_remove_manual_blocks(usuario_id, registro_ids)
