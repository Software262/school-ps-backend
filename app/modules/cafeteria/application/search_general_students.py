"""
Author: Danilo Castillejo
Role: Developer of the cafeteria module
"""

from app.core.db import SessionDep
from app.modules.cafeteria.domain.service import CafeteriaService
from app.modules.cafeteria.infrastructure.repository import CafeteriaRepository


class SearchGeneralStudents:
    def __init__(self, session: SessionDep):
        self.repository = CafeteriaRepository(session=session)
        self.service = CafeteriaService(repository=self.repository)

    async def execute(self, query: str | None = None, grado_id: int | None = None):
        """
        Executes the search logic via the domain service.
        """
        return await self.service.search_general_students_flat(query, grado_id)
