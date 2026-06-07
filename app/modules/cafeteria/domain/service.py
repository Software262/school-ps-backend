"""
Cafeteria Module Domain Service.
Author: Danilo Castillejo
"""

from datetime import datetime

from app.modules.cafeteria.domain.entities import (
    CafeteriaEntity,
    DebtorEntity,
    GradeEntity,
    StudentInfoEntity,
)
from app.modules.cafeteria.domain.repositories import CafeteriaRepositoryInterface
from app.modules.cafeteria.infrastructure.models import Cafeteria
from app.modules.enrollment.application.contracts import StudentQueryService


class CafeteriaService:
    def __init__(
        self,
        repository: CafeteriaRepositoryInterface,
        student_service: StudentQueryService,
    ):
        self.repository = repository
        self.student_service = student_service

    async def get_student_status(
        self, estudiante_id: int, periodo_id: int
    ) -> CafeteriaEntity | None:
        """Checks the status of a specific student and returns a domain entity."""
        record = await self.repository.get_by_student_and_period(
            estudiante_id, periodo_id
        )
        if not record:
            return None
        return CafeteriaEntity(
            id=record.id or 0,
            estudiante_id=record.estudiante_id,
            estado_cafeteria=record.estado_cafeteria,
            observaciones=record.observaciones,
        )

    async def get_status_list(self, periodo_id: int) -> list[DebtorEntity]:
        debtors_raw = await self.repository.get_all_debtors(periodo_id)
        if not debtors_raw:
            return []

        student_ids = [d.estudiante_id for d in debtors_raw]
        students_info = self.student_service.get_students_bulk(student_ids)
        students_map = {s.id: s for s in students_info}

        return [
            DebtorEntity(
                id=d.id or 0,
                estudiante_id=d.estudiante_id,
                nombre=students_map[d.estudiante_id].nombre
                if d.estudiante_id in students_map
                else "Desconocido",
                documento=students_map[d.estudiante_id].documento
                if d.estudiante_id in students_map
                else "N/A",
                grado=students_map[d.estudiante_id].grado_nombre
                if d.estudiante_id in students_map
                else "N/A",
                estado_cafeteria=d.estado_cafeteria,
                observaciones=d.observaciones or "",
            )
            for d in debtors_raw
        ]

    async def search_general_students_flat(
        self, query: str | None, grado_id: int | None
    ) -> list[StudentInfoEntity]:
        results = self.student_service.search_active_students(
            query=query.lower() if query else None, grado_id=grado_id, limit=15
        )
        return [
            StudentInfoEntity(
                id=s.id, nombre=s.nombre, documento=s.documento, grado=s.grado_nombre
            )
            for s in results
        ]

    async def get_all_grades_info(self) -> list[GradeEntity]:
        grades = self.student_service.get_all_grades()
        return [GradeEntity(id=g.id, nombre=g.nombre) for g in grades]

    async def format_report_data(self, periodo_id: int) -> list[list[str]]:
        data = await self.get_status_list(periodo_id)
        return [
            [
                r.documento,
                r.nombre,
                r.grado,
                "PAZ Y SALVO" if r.estado_cafeteria else "DEUDA",
                r.observaciones,
            ]
            for r in data
        ]

    async def create_manual_block(
        self, estudiante_id: int, periodo_id: int, usuario_id: int, obs: str
    ) -> CafeteriaEntity:
        record = await self.repository.get_by_student_and_period(
            estudiante_id, periodo_id
        )
        if not record:
            record = Cafeteria(estudiante_id=estudiante_id, periodo_id=periodo_id)
        record.estado_cafeteria = False
        record.observaciones = obs
        record.usuario_id = usuario_id
        record.updated_at = datetime.now()
        saved = await self.repository.save(record)
        return CafeteriaEntity(
            id=saved.id or 0,
            estudiante_id=saved.estudiante_id,
            estado_cafeteria=saved.estado_cafeteria,
            observaciones=saved.observaciones,
        )

    async def clear_debts_bulk(self, registro_ids: list[int], usuario_id: int) -> int:
        count = 0
        for rid in registro_ids:
            record = await self.repository.get_by_id(rid)
            if record:
                record.estado_cafeteria = True
                record.usuario_id = usuario_id
                record.updated_at = datetime.now()
                record.observaciones = (
                    f"Deuda solventada el {datetime.now().strftime('%Y-%m-%d %H:%M')}."
                )
                await self.repository.save(record)
                count += 1
        return count

    async def bulk_remove_manual_blocks(
        self, usuario_id: int, registro_ids: list[int]
    ) -> int:
        return await self.clear_debts_bulk(registro_ids, usuario_id)
