from app.core.db import SessionDep
from app.modules.enrollment.domain.service import EnrollmentService
from app.modules.enrollment.infrastructure.repository import (
    SQLEnrollmentRepository,
)


class ManualEnrollment:
    """Caso de uso: registrar y matricular manualmente a un estudiante."""

    def __init__(self, session: SessionDep) -> None:
        repository = SQLEnrollmentRepository(session)
        self.service = EnrollmentService(repository)

    def execute(
        self,
        documento: str,
        nombre: str,
        grado_str: str,
        nombre_acudiente: str,
        periodo_id: int,
        anio: int,
    ) -> int:
        return self.service.manual_enrollment(
            documento=documento,
            nombre=nombre,
            grado_str=grado_str,
            nombre_acudiente=nombre_acudiente,
            period_id=periodo_id,
            year=anio,
        )
