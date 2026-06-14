from sqlmodel import col, or_, select

from app.core.db import SessionDep
from app.modules.enrollment.infrastructure.models import (
    Complementario,
    Estudiante,
    Grado,
    Periodo,
)
from app.modules.training_schools.application.contracts import EnrollmentDataService
from app.modules.training_schools.domain.entities import (
    PeriodInfo,
    ProgramInfo,
    StudentInfo,
)


class EnrollmentAdapter(EnrollmentDataService):
    """Adapter that implements EnrollmentDataService using enrollment's DB models."""

    def __init__(self, session: SessionDep) -> None:
        self.session = session

    async def get_all_programs(self) -> list[ProgramInfo]:
        rows = self.session.exec(select(Complementario)).all()
        return [
            ProgramInfo(
                id=c.id if c.id is not None else 0,
                tipo_complementario=c.nombre,
                anio=c.anio,
                valor=c.valor,
                estado_complemento=c.estado_complemento,
            )
            for c in rows
        ]

    async def search_students(self, query: str) -> list[StudentInfo]:
        term = f"%{query}%"
        rows = self.session.exec(
            select(Estudiante)
            .where(
                or_(
                    col(Estudiante.documento).ilike(term),
                    col(Estudiante.nombre).ilike(term),
                )
            )
            .limit(20)
        ).all()
        return [
            StudentInfo(
                id=est.id if est.id is not None else 0,
                nombre=est.nombre,
                documento=est.documento,
                activo=est.activo,
            )
            for est in rows
        ]

    async def get_student_by_id(self, student_id: int) -> StudentInfo | None:
        result = self.session.exec(
            select(Estudiante, Grado)
            .join(Grado, col(Estudiante.grado_id) == col(Grado.id))
            .where(Estudiante.id == student_id)
        ).first()
        if not result:
            return None
        est, grado = result
        return StudentInfo(
            id=est.id if est.id is not None else 0,
            nombre=est.nombre,
            documento=est.documento,
            activo=est.activo,
            grado_nombre=grado.nombre,
        )

    async def get_periods(self) -> list[PeriodInfo]:
        rows = self.session.exec(select(Periodo).where(col(Periodo.estado))).all()
        return [
            PeriodInfo(
                id=p.id if p.id is not None else 0,
                periodo_electivo=p.periodo_electivo,
                estado=p.estado,
            )
            for p in rows
        ]
