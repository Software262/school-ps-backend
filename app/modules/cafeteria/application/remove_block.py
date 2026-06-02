"""
Cafeteria Module Remove Block Use Case.

Author: Danilo Castillejo
Role: Developer of the cafeteria module
"""

from app.core.db import SessionDep
from app.modules.cafeteria.domain.service import CafeteriaService
from app.modules.cafeteria.infrastructure.repository import CafeteriaRepository


class RemoveBlock:
    """Use case to remove manual blocks and set students back to 'Paz y Salvo'."""

    def __init__(self, session: SessionDep):
        self.repository = CafeteriaRepository(session=session)
        self.service = CafeteriaService(repository=self.repository)

    async def execute(self, registro_ids: list[int], usuario_id: int):
        return await self.service.bulk_remove_manual_blocks(usuario_id, registro_ids)
