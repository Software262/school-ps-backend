"""
Cafeteria Module Domain Repository Interface.

Author: Danilo Castillejo
Role: Developer of the cafeteria module
"""

from abc import ABC, abstractmethod
from app.modules.cafeteria.infrastructure.models import Cafeteria


class CafeteriaRepositoryInterface(ABC):
    """
    Abstract interface that defines the data access rules.
    To comply with decoupling rules, it only handles Cafeteria entities.
    """

    @abstractmethod
    async def get_all_by_period(self, periodo_id: int) -> list[Cafeteria]:
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
