from abc import ABC, abstractmethod
from app.modules.classroom.infrastructure.models import Pupitre


class PupitreRepository(ABC):
    # Se obtiene el pupitre al cual pertenece el estudiante, si no tiene pupitre se retorna None
    @abstractmethod
    async def get_student_desk(self, estudiante_id: int) -> Pupitre | None:
        pass

    # Se actualiza el estado de UN pupitre, se retorna el pupitre actualizado
    @abstractmethod
    async def update_desk_state(self, pupitre: Pupitre) -> Pupitre:
        pass

    # Se obtiene la lista de pupitres asociados a los estudiantes que pertenecen a un mismo grado, si no se encuentran pupitres se retorna None
    @abstractmethod
    async def list_desks_by_students(self, estudiante_ids: list[int]) -> list[Pupitre]:
        pass

    # Se actualiza el estado de varios pupitres, se retorna la cantidad de pupitres actualizados
    @abstractmethod
    async def bulk_update_desk_states(self, pupitres: list[Pupitre]) -> int:
        pass

    # Se crea un nuevo pupitre, se retorna el pupitre creado
    @abstractmethod
    async def add_desk(
        self, estudiante_id: int, estado_pupitre: bool, observacion: str | None
    ) -> Pupitre:
        pass
