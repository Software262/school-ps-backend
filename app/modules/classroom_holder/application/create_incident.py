from app.modules.classroom_holder.domain.entities import IncidenciaDomain
from app.modules.classroom_holder.domain.repositories import IncidenciaRepositoryInterface
from app.modules.classroom_holder.schemas.request import IncidenciaCreateRequest

class CreateIncidentUseCase:
    def __init__(self, repository: IncidenciaRepositoryInterface):
        self.repository = repository

    def execute(self, request: IncidenciaCreateRequest, current_docente_id: int) -> IncidenciaDomain:
        incidencia = IncidenciaDomain(
            id=None,
            estudiante_id=request.estudiante_id,
            docente_id=current_docente_id,
            tipo_incidencia=request.tipo_incidencia,
            descripcion=request.descripcion,
            fecha=request.fecha
        )
        return self.repository.save(incidencia)