from sqlmodel import col, select

from app.core.db import SessionDep
from app.modules.auth.infrastructure.models import Usuario
from app.modules.training_schools.domain.repositories import (
    TrainingSchoolRepositoryInterface,
)
from app.modules.training_schools.infrastructure.models import DetalleEscuelaFormacion


class TrainingSchoolRepository(TrainingSchoolRepositoryInterface):
    def __init__(self, session: SessionDep) -> None:
        self.session = session

    async def validate_user_exists(self, user_id: int) -> bool:
        return self.session.get(Usuario, user_id) is not None

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
        return self.session.exec(
            select(DetalleEscuelaFormacion).where(
                DetalleEscuelaFormacion.estudiante_id == estudiante_id,
                DetalleEscuelaFormacion.complementario_id == complementario_id,
                DetalleEscuelaFormacion.periodo_id == periodo_id,
            )
        ).first()

    async def get_enrollments_by_period(
        self, periodo_id: int
    ) -> list[DetalleEscuelaFormacion]:
        return list(
            self.session.exec(
                select(DetalleEscuelaFormacion).where(
                    DetalleEscuelaFormacion.periodo_id == periodo_id
                )
            ).all()
        )

    async def get_active_enrollments_by_student(
        self, estudiante_id: int
    ) -> list[DetalleEscuelaFormacion]:
        return list(
            self.session.exec(
                select(DetalleEscuelaFormacion).where(
                    DetalleEscuelaFormacion.estudiante_id == estudiante_id,
                    col(DetalleEscuelaFormacion.activo),
                )
            ).all()
        )

    async def save(
        self, enrollment: DetalleEscuelaFormacion
    ) -> DetalleEscuelaFormacion:
        self.session.add(enrollment)
        self.session.commit()
        self.session.refresh(enrollment)
        return enrollment
