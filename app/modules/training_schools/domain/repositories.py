from abc import ABC, abstractmethod

from app.modules.training_schools.infrastructure.models import DetalleEscuelaFormacion


class TrainingSchoolRepositoryInterface(ABC):
    @abstractmethod
    async def validate_user_exists(self, user_id: int) -> bool:
        pass

    @abstractmethod
    async def get_enrollment(
        self, enrollment_id: int
    ) -> DetalleEscuelaFormacion | None:
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
    async def get_active_enrollments_by_student(
        self, estudiante_id: int
    ) -> list[DetalleEscuelaFormacion]:
        pass

    @abstractmethod
    async def save(
        self, enrollment: DetalleEscuelaFormacion
    ) -> DetalleEscuelaFormacion:
        pass
