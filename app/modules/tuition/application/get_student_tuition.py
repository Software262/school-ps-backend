from app.modules.tuition.domain.service import TuitionService
from app.modules.tuition.domain.entities import TuitionAccount


class GetStudentTuitionUseCase:
    def __init__(self, service: TuitionService):
        self.service = service

    def execute(self, student_id: int) -> TuitionAccount | None:
        return self.service.get_student_account(student_id)
