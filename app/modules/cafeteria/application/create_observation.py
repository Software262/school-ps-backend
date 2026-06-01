"""
Cafeteria Module Create Observation (Manual Block) Use Case.

Author: Danilo Castillejo
Role: Developer of the cafeteria module
"""

from app.core.db import SessionDep
from app.modules.cafeteria.domain.service import CafeteriaService
from app.modules.cafeteria.infrastructure.repository import CafeteriaRepository


class CreateObservation:
    """Use case to handle manual debt blocking with mandatory observations."""

    def __init__(self, session: SessionDep):
        self.repository = CafeteriaRepository(session=session)
        self.service = CafeteriaService(repository=self.repository)

    async def execute(self, registro_id: int, usuario_id: int, obs: str):
        return await self.service.create_manual_block(registro_id, usuario_id, obs)
