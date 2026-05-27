from app.modules.classroom_holder.domain.repositories import IncidenciaRepositoryInterface

class ClassroomDomainService:
    def __init__(self, repository: IncidenciaRepositoryInterface):
        self.repository = repository

    def verificar_paz_y_salvo(self, estudiante_id: int) -> bool:
        """
        Regla crítica de negocio: Si el estudiante tiene al menos una 
        incidencia abierta en el salón, se bloquea su Paz y Salvo.
        """
        return not self.repository.has_open_incidents(estudiante_id)