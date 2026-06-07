from app.core.db import SessionDep
from app.modules.tests.domain.service import InternalTestService
from app.modules.tests.infrastructure.enrollment_adapter import EnrollmentAdapter
from app.modules.tests.infrastructure.repository import InternalTestRepository


class UpdateTestComplementary:
    """Actualiza el nombre y valor de un complementario de tipo prueba."""

    def __init__(self, session: SessionDep):
        self.service = InternalTestService(
            repository=InternalTestRepository(session),
            enrollment=EnrollmentAdapter(session),
        )

    async def execute(self, comp_id: int, tipo_complementario: str, valor: int) -> int:
        return await self.service.update_test_complementary(
            comp_id, tipo_complementario, valor
        )
