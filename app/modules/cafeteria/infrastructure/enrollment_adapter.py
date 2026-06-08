from sqlmodel import col, func, or_, select

from app.core.db import SessionDep
from app.modules.cafeteria.application.contracts import CafeteriaEnrollmentService
from app.modules.cafeteria.domain.entities import GradeEntity, StudentInfoEntity
from app.modules.enrollment.infrastructure.models import Estudiante, Grado


class CafeteriaEnrollmentAdapter(CafeteriaEnrollmentService):
    """Adapter that implements CafeteriaEnrollmentService using enrollment's DB models."""

    def __init__(self, session: SessionDep):
        self.session = session

    def search_active_students(
        self,
        query: str | None,
        grado_id: int | None,
        limit: int,
    ) -> list[StudentInfoEntity]:
        statement = (
            select(Estudiante, Grado)
            .join(Grado, col(Estudiante.grado_id) == col(Grado.id))
            .where(col(Estudiante.activo))
        )
        if query:
            q = f"%{query.strip().lower()}%"
            statement = statement.where(
                or_(
                    func.lower(Estudiante.nombre).like(q),
                    func.lower(Estudiante.documento).like(q),
                )
            )
        if grado_id is not None:
            statement = statement.where(col(Estudiante.grado_id) == grado_id)

        results = self.session.exec(statement.limit(limit)).all()
        return [
            StudentInfoEntity(
                id=e.id or 0,
                nombre=e.nombre,
                documento=e.documento,
                grado=g.nombre,
            )
            for e, g in results
            if e.id is not None
        ]

    def get_students_bulk(self, student_ids: list[int]) -> list[StudentInfoEntity]:
        if not student_ids:
            return []
        statement = (
            select(Estudiante, Grado)
            .join(Grado, col(Estudiante.grado_id) == col(Grado.id))
            .where(col(Estudiante.id).in_(student_ids))
        )
        results = self.session.exec(statement).all()
        return [
            StudentInfoEntity(
                id=e.id or 0,
                nombre=e.nombre,
                documento=e.documento,
                grado=g.nombre,
            )
            for e, g in results
            if e.id is not None
        ]

    def get_all_grades(self) -> list[GradeEntity]:
        results = self.session.exec(select(Grado).order_by(col(Grado.nombre))).all()
        return [
            GradeEntity(id=g.id or 0, nombre=g.nombre)
            for g in results
            if g.id is not None
        ]
