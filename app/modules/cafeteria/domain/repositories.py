from abc import ABC, abstractmethod
from app.modules.cafeteria.infrastructure.models import Cafeteria


class CafeteriaRepositoryInterface(ABC):
    @abstractmethod
    async def get_all_debtors(self, periodo_id: int) -> list[Cafeteria]:
        pass

    @abstractmethod
    async def get_by_id(self, registro_id: int) -> Cafeteria | None:
        pass

    @abstractmethod
    async def get_by_student_and_period(
        self, estudiante_id: int, periodo_id: int
    ) -> Cafeteria | None:
        pass

    @abstractmethod
    async def save(self, record: Cafeteria) -> Cafeteria:
        pass

    @abstractmethod
    async def get_multiple_by_ids(self, registro_ids: list[int]) -> list[Cafeteria]:
        pass
