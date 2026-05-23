from sqlmodel import Session
from app.modules.tuition.infrastructure.repositories import SQLModelTuitionRepository
from app.modules.tuition.domain.service import TuitionService
from app.modules.tuition.domain.entities import TuitionAccount


class GetStudentTuitionUseCase:
    def __init__(self, session: Session):
        repo = SQLModelTuitionRepository(session)
        self.service = TuitionService(repo)

    def execute(self, student_id: int) -> TuitionAccount | None:
        return self.service.get_student_account(student_id)
