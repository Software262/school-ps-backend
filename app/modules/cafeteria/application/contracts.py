from abc import ABC, abstractmethod

from app.modules.cafeteria.domain.entities import GradeEntity, StudentInfoEntity


class CafeteriaEnrollmentService(ABC):
    """Contract for enrollment-owned data that the cafeteria module needs."""

    @abstractmethod
    def search_active_students(
        self,
        query: str | None,
        grado_id: int | None,
        limit: int,
    ) -> list[StudentInfoEntity]:
        pass

    @abstractmethod
    def get_students_bulk(self, student_ids: list[int]) -> list[StudentInfoEntity]:
        pass

    @abstractmethod
    def get_all_grades(self) -> list[GradeEntity]:
        pass
