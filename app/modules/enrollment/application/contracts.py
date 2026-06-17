from abc import ABC, abstractmethod

class TuitionServiceContract(ABC):
    @abstractmethod
    def create_pension_account(self, student_id: int, grade_id: int, year: int) -> None:
        pass
