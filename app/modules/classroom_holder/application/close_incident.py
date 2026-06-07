from typing import Optional
from app.modules.classroom_holder.domain.entities import IncidenciaDomain
from app.modules.classroom_holder.domain.repositories import (
    IncidenciaRepositoryInterface,
)


class CloseIncidentUseCase:
    def __init__(self, repository: IncidenciaRepositoryInterface):
        self.repository = repository

    def execute(self, incident_id: int) -> Optional[IncidenciaDomain]:
        incidencia = self.repository.find_by_id(incident_id)
        if not incidencia:
            return None

        incidencia.cerrar()
        return self.repository.save(incidencia)
