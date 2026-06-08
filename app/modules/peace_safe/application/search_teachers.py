from app.core.db import SessionDep
from app.modules.peace_safe.domain.service import PeaceSafeService
from app.modules.peace_safe.infrastructure.repository import PeaceSafeRepository


class SearchTeachers:
    def __init__(self, session: SessionDep):
        self.service = PeaceSafeService(PeaceSafeRepository(session))

    async def execute(self, query: str) -> list[dict]:
        return self.service.search_teachers(query)
