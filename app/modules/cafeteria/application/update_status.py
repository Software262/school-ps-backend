"""
Cafeteria Module Update Status (Bulk) Use Case.

Author: Danilo Castillejo
Role: Developer of the cafeteria module
"""

from app.core.db import SessionDep
from app.modules.cafeteria.domain.service import CafeteriaService
from app.modules.cafeteria.infrastructure.repository import CafeteriaRepository


class UpdateStatus:
    """Use case to handle bulk 'Paz y Salvo' assignment while respecting manual blocks."""

    def __init__(self, session: SessionDep):
        self.repository = CafeteriaRepository(session=session)
        self.service = CafeteriaService(repository=self.repository)

    async def execute(
        self, periodo_id: int, estudiantes_ids: list[int], usuario_id: int
    ):
        return await self.service.bulk_update_paz_y_salvo(
            periodo_id, estudiantes_ids, usuario_id
        )
