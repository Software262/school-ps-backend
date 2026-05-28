"""
Author: Danilo Castillejo
Role: Developer of the cafeteria module
"""

from datetime import datetime
from app.modules.cafeteria.domain.repositories import CafeteriaRepositoryInterface
from app.modules.cafeteria.infrastructure.models import Cafeteria


class CafeteriaService:
    def __init__(self, repository: CafeteriaRepositoryInterface):
        self.repository = repository

    async def get_student_status(
        self, estudiante_id: int, periodo_id: int
    ) -> Cafeteria | None:
        return await self.repository.get_by_student_and_period(
            estudiante_id, periodo_id
        )

    async def format_report_data(self, periodo_id: int) -> list[list[str]]:
        """Logic for report formatting. Presentation strings live here."""
        records = await self.repository.get_all_by_period(periodo_id)
        report_rows = []
        for reg in records:
            status_text = "PAZ Y SALVO" if reg.estado_cafeteria else "DEUDA"
            report_rows.append(
                [str(reg.estudiante_id), status_text, reg.observaciones or ""]
            )
        return report_rows

    async def get_status_list(self, periodo_id: int) -> list[Cafeteria]:
        """Returns the list of cafeteria records."""
        return await self.repository.get_all_by_period(periodo_id)

    async def create_manual_block(
        self, registro_id: int, usuario_id: int, obs: str
    ) -> Cafeteria:
        if not obs or len(obs.strip()) < 5:
            raise ValueError("Observation is mandatory for manual blocks.")

        record = await self.repository.get_by_id(registro_id)
        if not record:
            raise ValueError("Record not found")

        record.estado_cafeteria = False
        record.observaciones = obs
        record.usuario_id = usuario_id
        record.updated_at = datetime.now()
        return await self.repository.save(record)

    async def bulk_update_paz_y_salvo(
        self, periodo_id: int, estudiantes_ids: list[int], usuario_id: int
    ) -> dict[str, int]:
        actualizados, excluidos = 0, 0
        for est_id in estudiantes_ids:
            record = await self.repository.get_by_student_and_period(est_id, periodo_id)
            if record and not record.estado_cafeteria:
                excluidos += 1
            elif record:
                record.estado_cafeteria = True
                record.usuario_id = usuario_id
                await self.repository.save(record)
                actualizados += 1

        return {
            "total_seleccionados": len(estudiantes_ids),
            "total_actualizados": actualizados,
            "total_excluidos": excluidos,
        }

    async def bulk_remove_manual_blocks(
        self, usuario_id: int, registro_ids: list[int]
    ) -> int:
        records = await self.repository.get_multiple_by_ids(registro_ids)
        count = 0
        for reg in records:
            reg.estado_cafeteria = True
            reg.usuario_id = usuario_id
            reg.observaciones = "Bloqueo retirado manualmente"
            await self.repository.save(reg)
            count += 1
        return count
