from app.core.db import SessionDep
from app.modules.tests.infrastructure.repository import InternalTestRepository
from app.modules.tests.domain.service import InternalTestService


class UpdateTestComplementary:
    """Actualiza el nombre y valor de un complementario de tipo prueba."""

    def __init__(self, session: SessionDep):
        self.repository = InternalTestRepository(session)
        self.service = InternalTestService(self.repository)

    async def execute(self, comp_id: int, tipo_complementario: str, valor: int) -> int:
        return await self.service.update_test_complementary(
            comp_id, tipo_complementario, valor
        )
