from app.modules.classroom_holder.domain.entities import IncidenciaDomain
from app.modules.classroom_holder.domain.service import ClassroomDomainService
from app.modules.classroom_holder.infrastructure.enrollment_adapter import (
    ClassroomEnrollmentAdapter,
)
from app.modules.classroom_holder.infrastructure.repository import IncidenciaRepository


class CloseIncident:
    def __init__(self, session):
        self.service = ClassroomDomainService(
            repository=IncidenciaRepository(session=session),
            enrollment=ClassroomEnrollmentAdapter(session=session),
        )

    def execute(self, incident_id: int) -> IncidenciaDomain | None:
        return self.service.cerrar_incidencia(incident_id)
