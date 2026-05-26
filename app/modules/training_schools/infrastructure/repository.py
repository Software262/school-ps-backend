from datetime import datetime
from typing import Sequence
from sqlalchemy import func
from sqlmodel import col, select

from app.core.db import SessionDep
from app.modules.training_schools.domain.repositories import (
    TrainingSchoolsRepository as TrainingSchoolsRepositoryInterface,
)
from app.modules.training_schools.infrastructure.models import DetalleEscuelaFormacion
from app.modules.enrollment.infrastructure.models import Estudiante, Complementario
from app.modules.training_schools.schemas.request import (
    CreateEnrollmentRequest,
    CreateProgramRequest,
)


class TrainingSchoolsRepository(TrainingSchoolsRepositoryInterface):
    def __init__(self, session: SessionDep):
        self.session = session

    async def get_student_by_id(self, student_id: int) -> Estudiante | None:
        return self.session.get(Estudiante, student_id)

    async def search_students(self, query: str) -> Sequence[Estudiante]:
        search = f"%{query.strip()}%"
        statement = select(Estudiante).where(
            Estudiante.activo == True,  # noqa: E712
            (
                col(Estudiante.nombre).ilike(search)
                | col(Estudiante.documento).ilike(search)
            ),
        )
        return self.session.exec(statement).all()

    async def get_complementario_by_id(
        self, complementario_id: int
    ) -> Complementario | None:
        return self.session.get(Complementario, complementario_id)

    async def get_available_programs(self) -> Sequence[Complementario]:
        statement = select(Complementario).where(
            func.lower(Complementario.estado_complemento) == "activo",
            Complementario.uso_matricula == False,  # noqa: E712
        )
        return self.session.exec(statement).all()

    async def get_program_by_name(self, nombre: str) -> Complementario | None:
        statement = select(Complementario).where(
            func.lower(Complementario.tipo_complementario) == nombre.strip().lower(),
            Complementario.uso_matricula == False,  # noqa: E712
        )
        return self.session.exec(statement).first()

    async def create_program(self, data: CreateProgramRequest) -> Complementario:
        program = Complementario(
            tipo_complementario=data.nombre.strip(),
            anio=datetime.now().year,
            valor=data.valor,
            estado_complemento="activo",
            uso_matricula=False,
        )
        self.session.add(program)
        self.session.commit()
        self.session.refresh(program)
        return program

    async def get_enrollment(
        self, student_id: int, complementario_id: int, mes: str
    ) -> DetalleEscuelaFormacion | None:
        statement = select(DetalleEscuelaFormacion).where(
            DetalleEscuelaFormacion.estudiante_id == student_id,
            DetalleEscuelaFormacion.complementario_id == complementario_id,
            DetalleEscuelaFormacion.mes == mes,
        )
        return self.session.exec(statement).first()

    async def create_enrollment(
        self, enrollment_data: CreateEnrollmentRequest
    ) -> DetalleEscuelaFormacion:
        new_enrollment = DetalleEscuelaFormacion(
            complementario_id=enrollment_data.complementario_id,
            estudiante_id=enrollment_data.estudiante_id,
            fecha_registro=datetime.now(),
            mes=enrollment_data.mes,
            activo=True,
            estado_escuela=False,  # Enrolled but unpaid by default
        )
        self.session.add(new_enrollment)
        self.session.commit()
        self.session.refresh(new_enrollment)
        return new_enrollment

    async def get_student_enrollments(
        self, student_id: int
    ) -> Sequence[DetalleEscuelaFormacion]:
        statement = select(DetalleEscuelaFormacion).where(
            DetalleEscuelaFormacion.estudiante_id == student_id
        )
        return self.session.exec(statement).all()

    async def get_enrollments_by_program(
        self, complementario_id: int
    ) -> Sequence[DetalleEscuelaFormacion]:
        statement = select(DetalleEscuelaFormacion).where(
            DetalleEscuelaFormacion.complementario_id == complementario_id
        )
        return self.session.exec(statement).all()

    async def get_enrollments(
        self,
        student_id: int | None = None,
        complementario_id: int | None = None,
        mes: str | None = None,
        activo: bool | None = None,
        estado_escuela: bool | None = None,
    ) -> Sequence[DetalleEscuelaFormacion]:
        statement = select(DetalleEscuelaFormacion)

        if student_id is not None:
            statement = statement.where(
                DetalleEscuelaFormacion.estudiante_id == student_id
            )
        if complementario_id is not None:
            statement = statement.where(
                DetalleEscuelaFormacion.complementario_id == complementario_id
            )
        if mes is not None:
            statement = statement.where(DetalleEscuelaFormacion.mes == mes)
        if activo is not None:
            statement = statement.where(DetalleEscuelaFormacion.activo == activo)
        if estado_escuela is not None:
            statement = statement.where(
                DetalleEscuelaFormacion.estado_escuela == estado_escuela
            )

        return self.session.exec(statement).all()

    async def save_enrollment(
        self, enrollment: DetalleEscuelaFormacion
    ) -> DetalleEscuelaFormacion:
        self.session.add(enrollment)
        self.session.commit()
        self.session.refresh(enrollment)
        return enrollment
