from app.core.db import SessionDep
from app.modules.enrollment.domain.service import EnrollmentService
from app.modules.enrollment.infrastructure.repository import (
    SQLEnrollmentRepository,
)


class CreateComplementary:
    """Caso de uso: crear un concepto complementario nuevo."""

    def __init__(self, session: SessionDep) -> None:
        repository = SQLEnrollmentRepository(session)
        self._service = EnrollmentService(repository)

    def execute(
        self,
        nombre: str,
        tipo_complementario_id: int,
        anio: int,
        valor: int,
        estado: str,
    ) -> int:
        return self._service.create_complementary(
            nombre=nombre,
            tipo_complementario_id=tipo_complementario_id,
            anio=anio,
            valor=valor,
            estado=estado,
        )
