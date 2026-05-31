from app.modules.classroom_holder.domain.entities import IncidenciaDomain
from app.modules.classroom_holder.domain.repositories import IncidenciaRepositoryInterface

class GetIncidentsUseCase:
    def __init__(self, repository: IncidenciaRepositoryInterface):
        self.repository = repository

    def execute(self, estudiante_id: int) -> list[IncidenciaDomain]:
        return self.repository.find_by_student(estudiante_id)
