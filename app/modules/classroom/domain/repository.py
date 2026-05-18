from abc import ABC, abstractmethod
from .entity import Pupitre

class PupitreRepository(ABC):

    @abstractmethod
    def obtener_por_estudiante(self, estudiante_id: int) -> Pupitre:
        pass

    @abstractmethod
    def guardar_pupitre(self, pupitre: Pupitre) -> Pupitre:
        pass

    @abstractmethod
    def obtener_por_grado(self, grado_id: int) -> list[Pupitre]:
        pass