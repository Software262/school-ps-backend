"""
Cafeteria Module Get Status Use Case.

Author: Danilo Castillejo
Role: Developer of the cafeteria module
"""

from app.core.db import SessionDep
from app.modules.cafeteria.domain.service import CafeteriaService
from app.modules.cafeteria.infrastructure.repository import CafeteriaRepository


class GetStatus:
    def __init__(self, session: SessionDep):
        self.repository = CafeteriaRepository(session=session)
        self.service = CafeteriaService(repository=self.repository)

    async def execute(self, periodo_id: int):
        # USAR EL SERVICIO PARA OBTENER LOS DATOS YA FORMATEADOS
        return await self.service.get_status_list(periodo_id)
