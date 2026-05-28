import io
import csv
from app.core.db import SessionDep
from app.modules.cafeteria.domain.service import CafeteriaService
from app.modules.cafeteria.infrastructure.repository import CafeteriaRepository


class ExportReport:
    def __init__(self, session: SessionDep):
        self.repository = CafeteriaRepository(session=session)
        self.service = CafeteriaService(repository=self.repository)

    async def execute(self, periodo_id: int) -> str:
        data_rows = await self.service.format_report_data(periodo_id)
        output = io.StringIO()  # type: ignore[abstract]
        writer = csv.writer(output)
        writer.writerow(["ID_ESTUDIANTE", "ESTADO", "OBSERVACIONES"])
        writer.writerows(data_rows)
        return output.getvalue()
