from app.core.db import SessionDep
from app.modules.tests.infrastructure.enrollment_adapter import EnrollmentAdapter


class CreateTestComplementary:
    def __init__(self, session: SessionDep):
        self.session = session
        self.enrollment = EnrollmentAdapter(session)

    async def execute(self, nombre: str, valor: int, anio: int) -> int:
        saved = await self.enrollment.create_complementary(
            nombre=nombre,
            valor=valor,
            anio=anio,
        )
        return saved.id
