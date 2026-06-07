from app.modules.classroom_holder.domain.entities import IncidenciaDomain
from app.modules.classroom_holder.domain.service import ClassroomDomainService
from app.modules.classroom_holder.infrastructure.enrollment_adapter import (
    ClassroomEnrollmentAdapter,
)
from app.modules.classroom_holder.infrastructure.repository import IncidenciaRepository
from app.modules.classroom_holder.schemas.request import IncidenciaCreateRequest


class CreateIncident:
    def __init__(self, session):
        self.service = ClassroomDomainService(
            repository=IncidenciaRepository(session=session),
            enrollment=ClassroomEnrollmentAdapter(session=session),
        )

    def execute(
        self, request: IncidenciaCreateRequest, current_docente_id: int
    ) -> IncidenciaDomain:
        return self.service.crear_incidencia(request, current_docente_id)
