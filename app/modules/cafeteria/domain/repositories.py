"""
Cafeteria Module Domain Repository Interface.

Author: Danilo Castillejo
Role: Developer of the cafeteria module
"""

from abc import ABC, abstractmethod
from app.modules.cafeteria.infrastructure.models import Cafeteria


class CafeteriaRepositoryInterface(ABC):
    @abstractmethod
    async def get_all_debtors(self, periodo_id: int) -> list:
        pass

    @abstractmethod
    async def search_general_students(
        self, query: str = "", grado_id: int | None = None
    ) -> list:
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

    @abstractmethod
    async def get_report_data(self, periodo_id: int) -> list:
        pass

    @abstractmethod
    async def get_all_grades(self) -> list:
        pass
