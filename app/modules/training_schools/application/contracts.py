from abc import ABC, abstractmethod

from app.modules.training_schools.domain.entities import (
    ComplementarioInfo,
    PeriodInfo,
    ProgramInfo,
    StudentInfo,
    TipoComplementarioInfo,
)


class EnrollmentDataService(ABC):
    """Contract for enrollment-owned data that the training_schools module needs."""

    @abstractmethod
    async def get_all_programs(self) -> list[ProgramInfo]:
        pass

    @abstractmethod
    async def search_students(self, query: str) -> list[StudentInfo]:
        pass

    @abstractmethod
    async def get_student_by_id(self, student_id: int) -> StudentInfo | None:
        pass

    @abstractmethod
    async def get_periods(self) -> list[PeriodInfo]:
        pass

    @abstractmethod
    async def list_tipos_complementario(self) -> list[TipoComplementarioInfo]:
        pass

    @abstractmethod
    async def get_tipo_complementario(
        self, tipo_id: int
    ) -> TipoComplementarioInfo | None:
        pass

    @abstractmethod
    async def create_tipo_complementario(
        self, nombre: str, sub_tipo_complementario: int | None
    ) -> TipoComplementarioInfo:
        pass

    @abstractmethod
    async def update_tipo_complementario(
        self,
        tipo_id: int,
        nombre: str | None,
        estado: bool | None,
        sub_tipo_complementario: int | None,
    ) -> TipoComplementarioInfo:
        pass

    @abstractmethod
    async def delete_tipo_complementario(self, tipo_id: int) -> None:
        pass

    @abstractmethod
    async def tipo_complementario_has_children_or_concepts(self, tipo_id: int) -> bool:
        pass

    @abstractmethod
    async def list_complementarios(self) -> list[ComplementarioInfo]:
        pass

    @abstractmethod
    async def get_complementario(
        self, complementario_id: int
    ) -> ComplementarioInfo | None:
        pass

    @abstractmethod
    async def create_complementario(
        self,
        nombre: str,
        anio: int,
        valor: int,
        estado_complemento: str,
        tipo_complementario_id: int,
    ) -> ComplementarioInfo:
        pass

    @abstractmethod
    async def update_complementario(
        self,
        complementario_id: int,
        nombre: str | None,
        anio: int | None,
        valor: int | None,
        estado_complemento: str | None,
        tipo_complementario_id: int | None,
    ) -> ComplementarioInfo:
        pass

    @abstractmethod
    async def delete_complementario(self, complementario_id: int) -> None:
        pass

    @abstractmethod
    async def complementario_has_references(self, complementario_id: int) -> bool:
        pass
