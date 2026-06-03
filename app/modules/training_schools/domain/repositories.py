from abc import ABC, abstractmethod

from app.modules.auth.infrastructure.models import Usuario
from app.modules.enrollment.infrastructure.models import Complementario, Estudiante, Grado, Periodo
from app.modules.training_schools.infrastructure.models import DetalleEscuelaFormacion


class TrainingSchoolRepositoryInterface(ABC):
    @abstractmethod
    async def get_all_programs(self) -> list[Complementario]:
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> Usuario | None:
        pass

    @abstractmethod
    async def search_students(self, query: str) -> list[Estudiante]:
        pass

    @abstractmethod
    async def get_student_by_id(self, student_id: int) -> Estudiante | None:
        pass

    @abstractmethod
    async def get_enrollment(self, enrollment_id: int) -> DetalleEscuelaFormacion | None:
        pass

    @abstractmethod
    async def get_enrollment_by_student_program_period(
        self,
        estudiante_id: int,
        complementario_id: int,
        periodo_id: int,
    ) -> DetalleEscuelaFormacion | None:
        pass

    @abstractmethod
    async def get_enrollments_by_period(
        self, periodo_id: int
    ) -> list[DetalleEscuelaFormacion]:
        pass

    @abstractmethod
    async def get_enrollments_with_students(
        self, periodo_id: int
    ) -> list[tuple[DetalleEscuelaFormacion, Estudiante, Grado]]:
        pass

    @abstractmethod
    async def get_active_enrollments_by_student(
        self, estudiante_id: int
    ) -> list[DetalleEscuelaFormacion]:
        pass

    @abstractmethod
    async def save(
        self, enrollment: DetalleEscuelaFormacion
    ) -> DetalleEscuelaFormacion:
        pass

    @abstractmethod
    async def get_periods(self) -> list[Periodo]:
        pass
