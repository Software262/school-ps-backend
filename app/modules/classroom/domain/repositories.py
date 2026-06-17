from abc import ABC, abstractmethod
from app.modules.classroom.infrastructure.models import DetallePupitre


class PupitreRepository(ABC):
    # Se obtiene el pupitre de un estudiante para un complementario específico (año vigente)
    @abstractmethod
    async def get_student_desk(
        self, estudiante_id: int, complementario_id: int
    ) -> DetallePupitre | None:
        pass

    # Se actualiza UN pupitre (confirmación de pago individual), se retorna el pupitre actualizado
    @abstractmethod
    async def update_desk(self, pupitre: DetallePupitre) -> DetallePupitre:
        pass

    # Se obtiene la lista de pupitres asociados a un grupo de estudiantes (ej. por curso)
    @abstractmethod
    async def list_desks_by_students(
        self, estudiante_ids: list[int]
    ) -> list[DetallePupitre]:
        pass

    # Se obtiene la lista de pupitres de todos los estudiantes de un grado
    @abstractmethod
    async def list_desks_by_grado_id(self, grado_id: int) -> list[DetallePupitre]:
        pass

    # Se actualiza el estado de varios pupitres, se retorna la cantidad de pupitres actualizados
    @abstractmethod
    async def bulk_update_desk_states(self, pupitres: list[DetallePupitre]) -> int:
        pass
