from app.modules.classroom_holder.application.contracts import (
    ClassroomEnrollmentService,
)
from app.modules.classroom_holder.domain.entities import (
    EstudianteResumen,
    IncidenciaDomain,
)
from app.modules.classroom_holder.domain.repositories import (
    IncidenciaRepositoryInterface,
)
from app.modules.classroom_holder.schemas.request import IncidenciaCreateRequest


class ClassroomDomainService:
    def __init__(
        self,
        repository: IncidenciaRepositoryInterface,
        enrollment: ClassroomEnrollmentService,
    ):
        self.repository = repository
        self.enrollment = enrollment

    def verificar_paz_y_salvo(self, estudiante_id: int) -> bool:
        return not self.repository.has_open_incidents(estudiante_id)

    def crear_incidencia(
        self, request: IncidenciaCreateRequest, current_docente_id: int
    ) -> IncidenciaDomain:
        incidencia = IncidenciaDomain(
            id=None,
            estudiante_id=request.estudiante_id,
            docente_id=current_docente_id,
            tipo_incidencia=request.tipo_incidencia,
            descripcion=request.descripcion,
            fecha=request.fecha,
        )
        return self.repository.save(incidencia)

    def cerrar_incidencia(self, incident_id: int) -> IncidenciaDomain | None:
        incidencia = self.repository.find_by_id(incident_id)
        if not incidencia:
            return None
        incidencia.cerrar()
        return self.repository.save(incidencia)

    def listar_por_estudiante(self, estudiante_id: int) -> list[IncidenciaDomain]:
        return self.repository.find_by_student(estudiante_id)

    def buscar_estudiantes(self, query: str) -> list[EstudianteResumen]:
        return self.enrollment.buscar_estudiantes_por_nombre(query)
