from app.modules.classroom_holder.domain.entities import IncidenciaDomain
from app.modules.classroom_holder.domain.service import ClassroomDomainService
from app.modules.classroom_holder.infrastructure.enrollment_adapter import (
    ClassroomEnrollmentAdapter,
)
from app.modules.classroom_holder.infrastructure.repository import IncidenciaRepository


class GetAllIncidents:
    def __init__(self, session):
        self.service = ClassroomDomainService(
            repository=IncidenciaRepository(session=session),
            enrollment=ClassroomEnrollmentAdapter(session=session),
        )

    def execute(self) -> list[IncidenciaDomain]:
        return self.service.listar_todas()
