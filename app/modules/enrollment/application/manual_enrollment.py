from app.core.db import SessionDep
from app.modules.enrollment.domain.service import EnrollmentService
from app.modules.enrollment.infrastructure.repository import (
    SQLEnrollmentRepository,
)
from app.modules.tuition.infrastructure.enrollment_adapter import (
    TuitionEnrollmentAdapter,
)


class ManualEnrollment:
    """Caso de uso: registrar y matricular manualmente a un estudiante."""

    def __init__(self, session: SessionDep) -> None:
        repository = SQLEnrollmentRepository(session)
        tuition_service = TuitionEnrollmentAdapter(session)
        self.service = EnrollmentService(repository, tuition_service)

    def execute(
        self,
        documento: str,
        nombre: str,
        grado_str: str,
        nombre_acudiente: str,
        periodo_id: int | None = None,
        anio: int = 2026,
    ) -> int:
        return self.service.manual_enrollment(
            documento=documento,
            nombre=nombre,
            grado_str=grado_str,
            nombre_acudiente=nombre_acudiente,
            period_id=periodo_id,
            year=anio,
        )
