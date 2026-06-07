from abc import ABC, abstractmethod
from typing import List, Optional
from app.modules.classroom_holder.domain.entities import IncidenciaDomain


class IncidenciaRepositoryInterface(ABC):
    @abstractmethod
    def save(self, incidencia: IncidenciaDomain) -> IncidenciaDomain:
        pass

    @abstractmethod
    def find_by_id(self, incidencia_id: int) -> Optional[IncidenciaDomain]:
        pass

    @abstractmethod
    def find_by_student(self, estudiante_id: int) -> List[IncidenciaDomain]:
        pass

    @abstractmethod
    def has_open_incidents(self, estudiante_id: int) -> bool:
        pass
