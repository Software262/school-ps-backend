from sqlmodel import Session, col, select

from app.modules.classroom_holder.application.contracts import (
    ClassroomEnrollmentService,
)
from app.modules.classroom_holder.domain.entities import EstudianteResumen
from app.modules.enrollment.infrastructure.models import Estudiante, Grado


class ClassroomEnrollmentAdapter(ClassroomEnrollmentService):
    """Adapter that implements ClassroomEnrollmentService using enrollment's DB models."""

    def __init__(self, session: Session):
        self.session = session

    def buscar_estudiantes_por_nombre(self, query: str) -> list[EstudianteResumen]:
        estudiantes = list(
            self.session.exec(
                select(Estudiante)
                .where(col(Estudiante.nombre).ilike(f"%{query}%"))
                .limit(10)
            ).all()
        )

        grado_ids = {e.grado_id for e in estudiantes}
        grados = (
            {
                g.id: g.nombre
                for g in self.session.exec(
                    select(Grado).where(col(Grado.id).in_(grado_ids))
                ).all()
            }
            if grado_ids
            else {}
        )

        return [
            EstudianteResumen(
                id=e.id or 0,
                nombre=e.nombre,
                grado_nombre=grados.get(e.grado_id, "Sin curso"),
            )
            for e in estudiantes
        ]
