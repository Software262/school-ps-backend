import io
import csv
from app.core.db import SessionDep
from app.modules.enrollment.infrastructure.repository import SQLEnrollmentRepository
from app.modules.enrollment.domain.service import StudentService
from app.modules.cafeteria.infrastructure.repository import CafeteriaRepository
from app.modules.cafeteria.domain.service import CafeteriaService


class ExportReport:
    def __init__(self, session: SessionDep):
        self.repository = CafeteriaRepository(session)
        enrollment_repo = SQLEnrollmentRepository(session)
        student_service = StudentService(enrollment_repo)
        self.service = CafeteriaService(self.repository, student_service)

    async def execute(self, periodo_id: int) -> str:
        data_rows = await self.service.format_report_data(periodo_id)
        output = io.StringIO()  # type: ignore[abstract]
        output.write("\ufeff")
        writer = csv.writer(output)
        writer.writerow(["DOCUMENTO", "ESTUDIANTE", "CURSO", "ESTADO", "OBSERVACIONES"])
        for row in data_rows:
            writer.writerow(row)
        return output.getvalue()
