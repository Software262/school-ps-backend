from app.core.db import SessionDep
from app.modules.tests.infrastructure.repository import InternalTestRepository
from app.modules.tests.domain.service import InternalTestService


class DeleteTestComplementary:
    """Elimina un complementario de tipo prueba y sus asignaciones asociadas."""

    def __init__(self, session: SessionDep):
        self.repository = InternalTestRepository(session)
        self.service = InternalTestService(self.repository)

    async def execute(self, comp_id: int):
        return await self.service.delete_test_complementary(comp_id)
