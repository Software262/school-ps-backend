from app.modules.classroom_holder.domain.entities import IncidenciaDomain
from app.modules.classroom_holder.domain.service import ClassroomDomainService
from app.modules.classroom_holder.infrastructure.enrollment_adapter import (
    ClassroomEnrollmentAdapter,
)
from app.modules.classroom_holder.infrastructure.repository import IncidenciaRepository


class GetIncidentsByStudent:
    def __init__(self, session):
        self.service = ClassroomDomainService(
            repository=IncidenciaRepository(session=session),
            enrollment=ClassroomEnrollmentAdapter(session=session),
        )

    def execute(self, estudiante_id: int) -> list[IncidenciaDomain]:
        return self.service.listar_por_estudiante(estudiante_id)
