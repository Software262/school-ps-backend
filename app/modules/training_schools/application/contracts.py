from abc import ABC, abstractmethod

from app.modules.training_schools.domain.entities import (
    PeriodInfo,
    ProgramInfo,
    StudentInfo,
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
