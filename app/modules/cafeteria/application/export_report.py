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
        results = await self.repository.get_report_data(periodo_id)
        output = io.StringIO()  # type: ignore
        writer = csv.writer(output)
        writer.writerow(["DOCUMENTO", "ESTUDIANTE", "CURSO", "ESTADO", "OBSERVACIONES"])

        for caf, est, grado in results:
            writer.writerow(
                [
                    est.documento,
                    est.nombre,
                    grado.nombre,
                    "PAZ Y SALVO" if caf.estado_cafeteria else "DEUDA",
                    caf.observaciones,
                ]
            )
        return output.getvalue()
