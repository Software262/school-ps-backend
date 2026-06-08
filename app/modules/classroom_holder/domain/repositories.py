from abc import ABC, abstractmethod
from app.modules.classroom_holder.domain.entities import IncidenciaDomain


class IncidenciaRepositoryInterface(ABC):
    @abstractmethod
    def save(self, incidencia: IncidenciaDomain) -> IncidenciaDomain:
        pass

    @abstractmethod
    def find_by_id(self, incidencia_id: int) -> IncidenciaDomain | None:
        pass

    @abstractmethod
    def find_by_student(self, estudiante_id: int) -> list[IncidenciaDomain]:
        pass

    @abstractmethod
    def find_all(self) -> list[IncidenciaDomain]:
        pass

    @abstractmethod
    def has_open_incidents(self, estudiante_id: int) -> bool:
        pass
