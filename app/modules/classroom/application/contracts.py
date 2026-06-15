# classroom/application/contracts.py
from abc import ABC, abstractmethod
from app.modules.classroom.domain.entities import (
    GradeEntity,
    StudentEntity,
    ComplementarioEntity,
)


class ClassroomEnrollmentService(ABC):
    """Contract for enrollment-owned data that the classroom module needs."""

    @abstractmethod
    def get_student_by_document(self, documento: str) -> StudentEntity | None: ...

    @abstractmethod
    def get_student_by_name(self, nombre: str) -> StudentEntity | None: ...

    @abstractmethod
    def get_students_by_grade(self, grado_id: int) -> list[StudentEntity]: ...

    @abstractmethod
    def get_grade(self, grado_id: int) -> GradeEntity | None: ...

    @abstractmethod
    def get_all_grades(self) -> list[GradeEntity]: ...

    @abstractmethod
    async def get_complementary_by_name(
        self, nombre: str
    ) -> ComplementarioEntity | None: ...
