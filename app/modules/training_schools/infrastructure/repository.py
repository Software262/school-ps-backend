from sqlmodel import or_, select

from app.core.db import SessionDep
from app.modules.auth.infrastructure.models import Usuario
from app.modules.enrollment.infrastructure.models import Complementario, Estudiante, Grado, Periodo
from app.modules.training_schools.domain.repositories import (
    TrainingSchoolRepositoryInterface,
)
from app.modules.training_schools.infrastructure.models import DetalleEscuelaFormacion


class TrainingSchoolRepository(TrainingSchoolRepositoryInterface):
    def __init__(self, session: SessionDep) -> None:
        self.session = session

    async def get_all_programs(self) -> list[Complementario]:
        # programs and their price (valor) are owned and configured by the
        # matrícula (enrollment) module as "complementario" records, created via
        # POST /api/v1/enrollment/complementary. this module only reads them.
        statement = select(Complementario)
        return list(self.session.exec(statement).all())

    async def get_user_by_id(self, user_id: int) -> Usuario | None:
        return self.session.get(Usuario, user_id)

    async def search_students(self, query: str) -> list[Estudiante]:
        term = f"%{query}%"
        statement = (
            select(Estudiante)
            .where(
                or_(
                    Estudiante.documento.ilike(term),  # type: ignore[union-attr]
                    Estudiante.nombre.ilike(term),  # type: ignore[union-attr]
                )
            )
            .limit(20)
        )
        return list(self.session.exec(statement).all())

    async def get_student_by_id(self, student_id: int) -> Estudiante | None:
        return self.session.get(Estudiante, student_id)

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
    ) -> list[tuple[DetalleEscuelaFormacion, Estudiante, Grado]]:
        statement = (
            select(DetalleEscuelaFormacion, Estudiante, Grado)
            .join(
                Estudiante,
                DetalleEscuelaFormacion.estudiante_id == Estudiante.id,  # type: ignore[arg-type]
            )
            .join(Grado, Estudiante.grado_id == Grado.id)  # type: ignore[arg-type]
            .where(DetalleEscuelaFormacion.periodo_id == periodo_id)
            .order_by(DetalleEscuelaFormacion.id)
        )
        rows = self.session.exec(statement).all()
        return [(enr, est, grado) for enr, est, grado in rows]

    async def get_active_enrollments_by_student(
        self, estudiante_id: int
    ) -> list[DetalleEscuelaFormacion]:
        statement = select(DetalleEscuelaFormacion).where(
            DetalleEscuelaFormacion.estudiante_id == estudiante_id,
            DetalleEscuelaFormacion.activo == True,  # noqa: E712
        )
        return list(self.session.exec(statement).all())

    async def save(
        self, enrollment: DetalleEscuelaFormacion
    ) -> DetalleEscuelaFormacion:
        self.session.add(enrollment)
        self.session.commit()
        self.session.refresh(enrollment)
        return enrollment

    async def get_periods(self) -> list[Periodo]:
        statement = select(Periodo).where(Periodo.estado == True)  # noqa: E712
        return list(self.session.exec(statement).all())
