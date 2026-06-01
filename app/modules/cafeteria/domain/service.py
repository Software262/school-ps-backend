"""
Author: Danilo Castillejo
Role: Developer of the cafeteria module
"""

from datetime import datetime
from typing import List, Dict, Any
from app.modules.cafeteria.domain.repositories import CafeteriaRepositoryInterface
from app.modules.cafeteria.infrastructure.models import Cafeteria


class CafeteriaService:
    def __init__(self, repository: CafeteriaRepositoryInterface):
        self.repository = repository

    async def get_student_status(
        self, estudiante_id: int, periodo_id: int
    ) -> Dict[str, Any] | None:
        """Checks the status of a specific student and flattens it."""
        record = await self.repository.get_by_student_and_period(
            estudiante_id, periodo_id
        )
        if not record:
            return None
        return {
            "id": record.id,
            "estudiante_id": record.estudiante_id,
            "estado_cafeteria": record.estado_cafeteria,
            "observaciones": record.observaciones or "",
        }

    async def get_status_list(self, periodo_id: int) -> List[Dict[str, Any]]:
        """Transforma las tuplas de DB en diccionarios planos para JSON."""
        results: List[Any] = await self.repository.get_all_debtors(periodo_id)
        # results viene como [(Cafeteria, Estudiante, Grado), ...]
        return [
            {
                "id": c.id,
                "estudiante_id": c.estudiante_id,
                "nombre": e.nombre,
                "documento": e.documento,
                "grado": g.nombre,
                "estado_cafeteria": c.estado_cafeteria,
                "observaciones": c.observaciones or "",
            }
            for c, e, g in results
        ]

    async def create_manual_block(
        self, estudiante_id: int, periodo_id: int, usuario_id: int, obs: str
    ) -> Dict[str, Any]:
        """Adds a new debtor and returns a dict."""
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
        return {
            "id": saved.id,
            "estudiante_id": saved.estudiante_id,
            "estado_cafeteria": saved.estado_cafeteria,
        }

    async def clear_debts_bulk(self, registro_ids: list[int], usuario_id: int) -> int:
        """CAF-RF-09: Clears debt for selected students."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        predefined_msg = (
            f"Deuda solventada el {now}. Trámite administrativo completado."
        )

        count = 0
        for rid in registro_ids:
            record = await self.repository.get_by_id(rid)
            if record:
                record.estado_cafeteria = True
                record.usuario_id = usuario_id
                record.observaciones = predefined_msg
                record.updated_at = datetime.now()
                await self.repository.save(record)
                count += 1
        return count

    async def bulk_remove_manual_blocks(
        self, usuario_id: int, registro_ids: list[int]
    ) -> int:
        """Alias para el caso de uso RemoveBlock."""
        return await self.clear_debts_bulk(registro_ids, usuario_id)

    async def search_general_students_flat(
        self, query: str | None = None, grado_id: int | None = None
    ) -> List[Dict[str, Any]]:
        """Aplana los datos de búsqueda general."""
        results: List[Any] = await self.repository.search_general_students(
            query or "", grado_id
        )
        return [
            {
                "id": e.id,
                "nombre": e.nombre,
                "documento": e.documento,
                "grado": g.nombre,
            }
            for e, g in results
        ]
