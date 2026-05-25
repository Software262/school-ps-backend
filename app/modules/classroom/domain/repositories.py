from abc import ABC, abstractmethod
from app.modules.classroom.infrastructure.models import Pupitre

class PupitreRepository(ABC):

    @abstractmethod
    async def obtener_por_estudiante(self, estudiante_id: int) -> Pupitre | None:
        pass

    @abstractmethod
    async def guardar_pupitre(self, pupitre: Pupitre) -> Pupitre:
        pass

    @abstractmethod
    async def obtener_por_grado(self, grado_id: int) -> list[Pupitre]:
        pass

    @abstractmethod
    async def guardar_muchos_pupitres(self, pupitres: list[Pupitre]) -> int:
        pass