from abc import ABC, abstractmethod

from app.modules.enrollment.infrastructure.models import Complementario, Estudiante
from app.modules.tests.infrastructure.models import DetallePrueba
from app.modules.tests.schemas.request import (
    CreateTestDetailRequest,
    UpdateTestDetailRequest,
)


class InternalTestRepository(ABC):
    @abstractmethod
    async def get_tests_pagination(self, offset: int, limit: int) -> list[dict]:
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
    ) -> list[dict]:
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

    @abstractmethod
    async def assign_massive(
        self, requests: list[CreateTestDetailRequest]
    ) -> list[DetallePrueba]:
        pass

    @abstractmethod
    async def get_active_students_by_grade(self, grado_id: int) -> list[Estudiante]:
        pass

    @abstractmethod
    async def get_available_tests(self) -> list[Complementario]:
        pass

    @abstractmethod
    async def get_existing_assignments(
        self, complementario_id: int, periodo_id: int
    ) -> list[int]:
        pass

    @abstractmethod
    async def get_complementary_by_id(self, comp_id: int) -> Complementario | None:
        pass

    @abstractmethod
    async def delete_test_complementary(self, comp_id: int) -> bool:
        pass

    @abstractmethod
    async def save_complementary(self, comp: Complementario) -> Complementario:
        pass

    @abstractmethod
    async def delete_test(self, test: DetallePrueba) -> bool:
        pass

    @abstractmethod
    async def save_test(self, test: DetallePrueba) -> DetallePrueba:
        pass
