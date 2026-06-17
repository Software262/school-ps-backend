from abc import ABC, abstractmethod

from app.modules.tests.domain.entities import (
    ComplementarioEntity,
    EstudianteEntity,
    GradoEntity,
    PeriodoEntity,
)


class EnrollmentDataService(ABC):
    """Contract for enrollment-owned data that the tests module needs."""

    @abstractmethod
    async def get_all_grados(self) -> list[GradoEntity]:
        pass

    @abstractmethod
    async def get_all_periodos(self) -> list[PeriodoEntity]:
        pass

    @abstractmethod
    async def get_all_estudiantes(self) -> list[EstudianteEntity]:
        pass

    @abstractmethod
    async def get_active_students_by_grade(
        self, grado_id: int
    ) -> list[EstudianteEntity]:
        pass

    @abstractmethod
    async def get_student_by_id(self, student_id: int) -> EstudianteEntity | None:
        pass

    @abstractmethod
    async def get_available_tests(self) -> list[ComplementarioEntity]:
        pass

    @abstractmethod
    async def get_complementary_by_id(
        self, comp_id: int
    ) -> ComplementarioEntity | None:
        pass

    @abstractmethod
    async def create_complementary(
        self, nombre: str, valor: int, anio: int
    ) -> ComplementarioEntity:
        pass

    @abstractmethod
    async def save_complementary(
        self, comp: ComplementarioEntity
    ) -> ComplementarioEntity:
        pass

    @abstractmethod
    async def delete_complementary(self, comp_id: int) -> bool:
        pass
