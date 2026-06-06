from sqlmodel import col, or_, select

from app.core.db import SessionDep
from app.modules.auth.infrastructure.models import Usuario
from app.modules.enrollment.infrastructure.models import (
    Complementario,
    Estudiante,
    Grado,
    Periodo,
)
from app.modules.training_schools.domain.entities import (
    PeriodInfo,
    ProgramInfo,
    StudentInfo,
)
from app.modules.training_schools.domain.repositories import (
    TrainingSchoolRepositoryInterface,
)
from app.modules.training_schools.infrastructure.models import DetalleEscuelaFormacion


class TrainingSchoolRepository(TrainingSchoolRepositoryInterface):
    def __init__(self, session: SessionDep) -> None:
        self.session = session

    async def get_all_programs(self) -> list[ProgramInfo]:
        # programs and their price (valor) are owned and configured by the
        # matrícula (enrollment) module as "complementario" records, created via
        # POST /api/v1/enrollment/complementary. this module only reads them.
        rows = list(self.session.exec(select(Complementario)).all())
        return [
            ProgramInfo(
                id=c.id if c.id is not None else 0,
                tipo_complementario=c.tipo_complementario,
                anio=c.anio,
                valor=c.valor,
                estado_complemento=c.estado_complemento,
                uso_matricula=c.uso_matricula,
            )
            for c in rows
        ]

    async def validate_user_exists(self, user_id: int) -> bool:
        return self.session.get(Usuario, user_id) is not None

    async def search_students(self, query: str) -> list[StudentInfo]:
        term = f"%{query}%"
        statement = (
            select(Estudiante)
            .where(
                or_(
                    col(Estudiante.documento).ilike(term),
                    col(Estudiante.nombre).ilike(term),
                )
            )
            .limit(20)
        )
        rows = list(self.session.exec(statement).all())
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
        est = self.session.get(Estudiante, student_id)
        if est is None:
            return None
        return StudentInfo(
            id=est.id if est.id is not None else 0,
            nombre=est.nombre,
            documento=est.documento,
            activo=est.activo,
        )

    async def get_enrollment(
        self, enrollment_id: int
    ) -> DetalleEscuelaFormacion | None:
        return self.session.get(DetalleEscuelaFormacion, enrollment_id)

    async def get_enrollment_by_student_program_period(
        self,
        estudiante_id: int,
        complementario_id: int,
        periodo_id: int,
    ) -> DetalleEscuelaFormacion | None:
        statement = select(DetalleEscuelaFormacion).where(
            DetalleEscuelaFormacion.estudiante_id == estudiante_id,
            DetalleEscuelaFormacion.complementario_id == complementario_id,
            DetalleEscuelaFormacion.periodo_id == periodo_id,
        )
        return self.session.exec(statement).first()

    async def get_enrollments_by_period(
        self, periodo_id: int
    ) -> list[DetalleEscuelaFormacion]:
        statement = select(DetalleEscuelaFormacion).where(
            DetalleEscuelaFormacion.periodo_id == periodo_id
        )
        return list(self.session.exec(statement).all())

    async def get_enrollments_with_students(
        self, periodo_id: int
    ) -> list[tuple[DetalleEscuelaFormacion, StudentInfo]]:
        statement = (
            select(DetalleEscuelaFormacion, Estudiante, Grado)
            .join(
                Estudiante,
                col(DetalleEscuelaFormacion.estudiante_id) == col(Estudiante.id),
            )
            .join(Grado, col(Estudiante.grado_id) == col(Grado.id))
            .where(DetalleEscuelaFormacion.periodo_id == periodo_id)
            .order_by(col(DetalleEscuelaFormacion.id))
        )
        rows = self.session.exec(statement).all()
        return [
            (
                enr,
                StudentInfo(
                    id=est.id if est.id is not None else 0,
                    nombre=est.nombre,
                    documento=est.documento,
                    activo=est.activo,
                    grado_nombre=grado.nombre,
                ),
            )
            for enr, est, grado in rows
        ]

    async def get_active_enrollments_by_student(
        self, estudiante_id: int
    ) -> list[DetalleEscuelaFormacion]:
        statement = select(DetalleEscuelaFormacion).where(
            DetalleEscuelaFormacion.estudiante_id == estudiante_id,
            col(DetalleEscuelaFormacion.activo),
        )
        return list(self.session.exec(statement).all())

    async def save(
        self, enrollment: DetalleEscuelaFormacion
    ) -> DetalleEscuelaFormacion:
        self.session.add(enrollment)
        self.session.commit()
        self.session.refresh(enrollment)
        return enrollment

    async def get_periods(self) -> list[PeriodInfo]:
        statement = select(Periodo).where(col(Periodo.estado))
        rows = list(self.session.exec(statement).all())
        return [
            PeriodInfo(
                id=p.id if p.id is not None else 0,
                periodo_electivo=p.periodo_electivo,
                estado=p.estado,
            )
            for p in rows
        ]
