"""
Cafeteria Module Get Status Use Case.

Author: Danilo Castillejo
Role: Developer of the cafeteria module
"""

from app.core.db import SessionDep
from app.modules.cafeteria.domain.service import CafeteriaService
from app.modules.cafeteria.infrastructure.repository import CafeteriaRepository


class GetStatus:
    """Use case to retrieve the full list of students and their cafeteria status."""

    def __init__(self, session: SessionDep):
        self.repository = CafeteriaRepository(session=session)
        self.service = CafeteriaService(repository=self.repository)

    async def execute(self, periodo_id: int):
        # The service handles the synchronization logic before returning the list
        return await self.service.get_status_list(periodo_id)
