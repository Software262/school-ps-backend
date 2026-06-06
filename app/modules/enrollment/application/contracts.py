from abc import ABC, abstractmethod

from app.modules.enrollment.schemas.response import (
    GradeResponse,
    StudentGeneralResponse,
    StudentResponse,
)


class StudentQueryService(ABC):
    @abstractmethod
    def search_active_students(
        self,
        query: str | None = None,
        grado_id: int | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[StudentGeneralResponse]:
        pass

    @abstractmethod
    def get_students_bulk(self, student_ids: list[int]) -> list[StudentGeneralResponse]:
        pass

    @abstractmethod
    def get_all_grades(self) -> list[GradeResponse]:
        pass

    @abstractmethod
    def get_student_by_id(self, student_id: int) -> StudentResponse | None:
        pass

    @abstractmethod
    def get_students_by_grade(self, grado_id: int) -> list[StudentResponse]:
        pass
