from app.modules.classroom_holder.domain.entities import EstudianteResumen
from app.modules.classroom_holder.domain.service import ClassroomDomainService
from app.modules.classroom_holder.infrastructure.enrollment_adapter import (
    ClassroomEnrollmentAdapter,
)
from app.modules.classroom_holder.infrastructure.repository import IncidenciaRepository


class SearchStudents:
    def __init__(self, session):
        self.service = ClassroomDomainService(
            repository=IncidenciaRepository(session=session),
            enrollment=ClassroomEnrollmentAdapter(session=session),
        )

    def execute(self, query: str) -> list[EstudianteResumen]:
        return self.service.buscar_estudiantes(query)
