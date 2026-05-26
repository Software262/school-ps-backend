from sqlmodel import Session

from app.modules.enrollment.domain.service import EnrollmentService
from app.modules.enrollment.infrastructure.repository import (
    SQLEnrollmentRepository,
)


class CreateComplementary:
    """Caso de uso: crear un concepto complementario nuevo."""

    def __init__(self, session: Session) -> None:
        repository = SQLEnrollmentRepository(session)
        self._service = EnrollmentService(repository)

    def execute(
        self,
        tipo_complementario: str,
        anio: int,
        valor: int,
        estado: str,
        uso_matricula: bool,
    ) -> int:
        return self._service.create_complementary(
            tipo_complementario=tipo_complementario,
            anio=anio,
            valor=valor,
            estado=estado,
            uso_matricula=uso_matricula,
        )
