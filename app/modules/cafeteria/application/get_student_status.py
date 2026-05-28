"""
Cafeteria Module Get Individual Student Status Use Case.

Author: Danilo Castillejo
Role: Developer of the cafeteria module
"""

from app.core.db import SessionDep
from app.modules.cafeteria.domain.service import CafeteriaService
from app.modules.cafeteria.infrastructure.repository import CafeteriaRepository


class GetStudentStatus:
    def __init__(self, session: SessionDep):
        self.repository = CafeteriaRepository(session=session)
        self.service = CafeteriaService(repository=self.repository)

    async def execute(self, estudiante_id: int, periodo_id: int):
        return await self.service.get_student_status(estudiante_id, periodo_id)
