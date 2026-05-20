from typing import Optional
from app.modules.tuition.domain.repositories import TuitionRepository
from app.modules.tuition.domain.entities import TuitionAccount


class GetStudentTuitionUseCase:
    def __init__(self, repository: TuitionRepository):
        self.repository = repository

    def execute(self, student_id: int) -> Optional[TuitionAccount]:
        return self.repository.get_account_by_student_id(student_id)
