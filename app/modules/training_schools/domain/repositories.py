from abc import ABC, abstractmethod
from typing import Sequence
from app.modules.training_schools.infrastructure.models import DetalleEscuelaFormacion
from app.modules.enrollment.infrastructure.models import Estudiante, Complementario
from app.modules.training_schools.schemas.request import (
    CreateEnrollmentRequest,
    CreateProgramRequest,
)


class TrainingSchoolsRepository(ABC):
    @abstractmethod
    async def get_student_by_id(self, student_id: int) -> Estudiante | None:
        pass

    @abstractmethod
    async def search_students(self, query: str) -> Sequence[Estudiante]:
        pass

    @abstractmethod
    async def get_complementario_by_id(
        self, complementario_id: int
    ) -> Complementario | None:
        pass

    @abstractmethod
    async def get_available_programs(self) -> Sequence[Complementario]:
        pass

    @abstractmethod
    async def get_program_by_name(self, nombre: str) -> Complementario | None:
        pass

    @abstractmethod
    async def create_program(self, data: CreateProgramRequest) -> Complementario:
        pass

    @abstractmethod
    async def get_enrollment(
        self, student_id: int, complementario_id: int, mes: str
    ) -> DetalleEscuelaFormacion | None:
        pass

    @abstractmethod
    async def create_enrollment(
        self, enrollment_data: CreateEnrollmentRequest
    ) -> DetalleEscuelaFormacion:
        pass

    @abstractmethod
    async def get_student_enrollments(
        self, student_id: int
    ) -> Sequence[DetalleEscuelaFormacion]:
        pass

    @abstractmethod
    async def get_enrollments_by_program(
        self, complementario_id: int
    ) -> Sequence[DetalleEscuelaFormacion]:
        pass

    @abstractmethod
    async def get_enrollments(
        self,
        student_id: int | None = None,
        complementario_id: int | None = None,
        mes: str | None = None,
        activo: bool | None = None,
        estado_escuela: bool | None = None,
    ) -> Sequence[DetalleEscuelaFormacion]:
        pass

    @abstractmethod
    async def save_enrollment(
        self, enrollment: DetalleEscuelaFormacion
    ) -> DetalleEscuelaFormacion:
        pass
