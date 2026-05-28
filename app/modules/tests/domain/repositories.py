from abc import ABC, abstractmethod
from typing import Sequence

from app.modules.tests.infrastructure.models import DetallePrueba
from app.modules.tests.schemas.request import (
    CreateTestDetailRequest,
    UpdateTestDetailRequest,
)


class InternalTestRepository(ABC):
    @abstractmethod
    async def get_tests_pagination(
        self, offset: int, limit: int
    ) -> Sequence[DetallePrueba]:
        pass

    @abstractmethod
    async def get_test_by_id(self, test_id: int) -> DetallePrueba | None:
        pass

    @abstractmethod
    async def get_tests_by_student(
        self,
        student_id: int,
        offset: int,
        limit: int,
    ) -> Sequence[DetallePrueba]:
        pass

    @abstractmethod
    async def create_test(self, test_data: CreateTestDetailRequest) -> DetallePrueba:
        pass

    @abstractmethod
    async def update_test(
        self,
        test: DetallePrueba,
        test_data: UpdateTestDetailRequest,
    ) -> DetallePrueba:
        pass
