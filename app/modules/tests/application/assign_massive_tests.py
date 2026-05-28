from sqlmodel import select
from app.core.db import SessionDep
from app.modules.tests.infrastructure.repository import InternalTestRepository
from app.modules.tests.infrastructure.models import DetallePrueba
from app.modules.tests.schemas.request import (
    MassiveAssignmentRequest,
    CreateTestDetailRequest,
)


class AssignMassiveTests:
    def __init__(self, session: SessionDep):
        self.repository = InternalTestRepository(session)
        self.session = session

    async def execute(self, request: MassiveAssignmentRequest):
        students = await self.repository.get_active_students_by_grade(request.grado_id)
        if not students:
            return {
                "assigned": [],
                "skipped": 0,
                "message": "No hay estudiantes activos en este grado",
            }

        # IDs que ya tienen esta prueba asignada
        existing_ids = set(
            self.session.exec(
                select(DetallePrueba.estudiante_id).where(
                    DetallePrueba.complementario_id == request.complementario_id
                )
            ).all()
        )

        new_students = [s for s in students if s.id not in existing_ids]
        skipped = len(students) - len(new_students)

        if not new_students:
            return {
                "assigned": [],
                "skipped": skipped,
                "message": f"Todos los estudiantes ({skipped}) ya tienen esta prueba asignada",
            }

        reqs = [
            CreateTestDetailRequest(
                estudiante_id=s.id,
                complementario_id=request.complementario_id,
                tipo_prueba=request.tipo_prueba,
                estado="pendiente",
                valor_pagado=0,
                periodo_id=request.periodo_id,
            )
            for s in new_students
        ]

        assigned = await self.repository.assign_massive(reqs)
        return {
            "assigned": [{"id": a.id} for a in assigned],
            "skipped": skipped,
            "message": f"Se asignaron {len(assigned)} pruebas. {skipped} estudiante(s) ya la tenían.",
        }
