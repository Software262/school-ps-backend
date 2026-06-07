from abc import ABC, abstractmethod

from app.modules.inventory.domain.entities import StudentEntity


class InventoryEnrollmentService(ABC):
    """Contract for enrollment-owned data that the inventory module needs."""

    @abstractmethod
    def get_student_by_id(self, student_id: int) -> StudentEntity | None:
        pass
