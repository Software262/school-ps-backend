import csv
import io

from app.core.db import SessionDep
from app.modules.cafeteria.domain.service import CafeteriaService
from app.modules.cafeteria.infrastructure.enrollment_adapter import (
    CafeteriaEnrollmentAdapter,
)
from app.modules.cafeteria.infrastructure.repository import CafeteriaRepository


class ExportReport:
    def __init__(self, session: SessionDep):
        self.service = CafeteriaService(
            repository=CafeteriaRepository(session),
            student_service=CafeteriaEnrollmentAdapter(session),
        )

    async def execute(self, periodo_id: int) -> str:
        data_rows = await self.service.format_report_data(periodo_id)
        output = io.StringIO()  # type: ignore[abstract]
        output.write("﻿")
        writer = csv.writer(output)
        writer.writerow(["DOCUMENTO", "ESTUDIANTE", "CURSO", "ESTADO", "OBSERVACIONES"])
        for row in data_rows:
            writer.writerow(row)
        return output.getvalue()
