from datetime import datetime
from typing import Sequence
from app.modules.training_schools.domain.repositories import TrainingSchoolsRepository
from app.modules.training_schools.infrastructure.models import DetalleEscuelaFormacion
from app.modules.training_schools.schemas.request import (
    CreateEnrollmentRequest,
    RegisterPaymentRequest,
    UnsubscribeRequest,
    CreateProgramRequest,
)


class TrainingSchoolsService:
    def __init__(self, repository: TrainingSchoolsRepository):
        self.repository = repository

    async def list_available_programs(self):
        return await self.repository.get_available_programs()

    async def create_program(self, data: CreateProgramRequest):
        existing = await self.repository.get_program_by_name(data.nombre)
        if existing:
            return None
        return await self.repository.create_program(data)

    async def search_students(self, query: str):
        return await self.repository.search_students(query)

    async def enroll_student(
        self, data: CreateEnrollmentRequest
    ) -> DetalleEscuelaFormacion | None:
        # Validate student existence
        student = await self.repository.get_student_by_id(data.estudiante_id)
        if not student:
            return None
        if not getattr(student, "activo", True):
            return None

        # Validate program existence
        program = await self.repository.get_complementario_by_id(data.complementario_id)
        if not program:
            return None

        # Validate program is active
        # The ERS mentions checking if program is active ("programa activo")
        if program.estado_complemento.lower() != "activo":
            return None

        data.mes = data.mes.strip().lower()

        # Validate no duplicate monthly record for the same student/program/month.
        existing = await self.repository.get_enrollment(
            student_id=data.estudiante_id,
            complementario_id=data.complementario_id,
            mes=data.mes,
        )
        if existing:
            # Already enrolled
            return None

        # Create enrollment
        return await self.repository.create_enrollment(data)

    async def register_payment(
        self, data: RegisterPaymentRequest
    ) -> DetalleEscuelaFormacion | None:
        data.mes = data.mes.strip().lower()

        # Retrieve the monthly record
        enrollment = await self.repository.get_enrollment(
            student_id=data.estudiante_id,
            complementario_id=data.complementario_id,
            mes=data.mes,
        )
        if not enrollment:
            return None

        # Check if already paid or inactive
        if not enrollment.activo:
            return None

        # Mark the administrative monthly payment as completed.
        enrollment.estado_escuela = True
        enrollment.updated_at = datetime.now()
        return await self.repository.save_enrollment(enrollment)

    async def unmark_payment(
        self, data: RegisterPaymentRequest
    ) -> DetalleEscuelaFormacion | None:
        data.mes = data.mes.strip().lower()

        enrollment = await self.repository.get_enrollment(
            student_id=data.estudiante_id,
            complementario_id=data.complementario_id,
            mes=data.mes,
        )
        if not enrollment:
            return None

        if not enrollment.activo:
            return None

        enrollment.estado_escuela = False
        enrollment.updated_at = datetime.now()
        return await self.repository.save_enrollment(enrollment)

    async def unsubscribe_student(
        self,
        student_id: int,
        complementario_id: int,
        mes: str,
        data: UnsubscribeRequest,
    ) -> DetalleEscuelaFormacion | None:
        mes = mes.strip().lower()

        # Retrieve the monthly record
        enrollment = await self.repository.get_enrollment(
            student_id=student_id, complementario_id=complementario_id, mes=mes
        )
        if not enrollment:
            return None

        # Mark as inactive and persist the unsubscribe reason
        enrollment.activo = False
        enrollment.motivo_baja = data.motivo
        enrollment.updated_at = datetime.now()
        return await self.repository.save_enrollment(enrollment)

    async def unsubscribe_student_from_program(
        self, student_id: int, complementario_id: int, data: UnsubscribeRequest
    ) -> Sequence[DetalleEscuelaFormacion]:
        enrollments = await self.repository.get_enrollments(
            student_id=student_id,
            complementario_id=complementario_id,
            activo=True,
        )
        for enrollment in enrollments:
            enrollment.activo = False
            enrollment.motivo_baja = data.motivo
            enrollment.updated_at = datetime.now()
            await self.repository.save_enrollment(enrollment)
        return enrollments

    async def get_student_status(self, student_id: int) -> dict:
        student = await self.repository.get_student_by_id(student_id)
        if not student:
            return {
                "estudiante_id": student_id,
                "paz_y_salvo": False,
                "detalle": "El estudiante no existe.",
            }

        enrollments = await self.repository.get_student_enrollments(student_id)

        # Filter active enrollments
        active_enrollments = [e for e in enrollments if e.activo]

        # If any active enrollment has estado_escuela = False (unpaid), they are blocked
        unpaid = []
        for e in active_enrollments:
            if not e.estado_escuela:
                # We can fetch the program name
                program = await self.repository.get_complementario_by_id(
                    e.complementario_id
                )
                program_name = (
                    program.tipo_complementario
                    if program
                    else f"Programa #{e.complementario_id}"
                )
                unpaid.append(f"{program_name} ({e.mes})")

        if unpaid:
            return {
                "estudiante_id": student_id,
                "paz_y_salvo": False,
                "detalle": f"Mensualidades pendientes en: {', '.join(unpaid)}",
            }

        return {
            "estudiante_id": student_id,
            "paz_y_salvo": True,
            "detalle": "Paz y salvo en todas las escuelas de formacion activas.",
        }

    async def list_student_enrollments(
        self, student_id: int
    ) -> Sequence[DetalleEscuelaFormacion]:
        return await self.repository.get_student_enrollments(student_id)

    async def list_program_enrollments(
        self, complementario_id: int
    ) -> Sequence[DetalleEscuelaFormacion]:
        return await self.repository.get_enrollments_by_program(complementario_id)

    async def list_enrollments(
        self,
        student_id: int | None = None,
        complementario_id: int | None = None,
        mes: str | None = None,
        activo: bool | None = None,
        estado_escuela: bool | None = None,
    ) -> Sequence[DetalleEscuelaFormacion]:
        return await self.repository.get_enrollments(
            student_id=student_id,
            complementario_id=complementario_id,
            mes=mes.strip().lower() if mes else None,
            activo=activo,
            estado_escuela=estado_escuela,
        )

    async def get_monthly_status(self, student_id: int, complementario_id: int) -> dict:
        enrollments = await self.repository.get_enrollments(
            student_id=student_id,
            complementario_id=complementario_id,
        )
        active_enrollments = [e for e in enrollments if e.activo]
        unpaid = [e.mes for e in active_enrollments if not e.estado_escuela]

        return {
            "estudiante_id": student_id,
            "complementario_id": complementario_id,
            "paz_y_salvo": len(unpaid) == 0,
            "detalle": (
                "Paz y salvo en la disciplina."
                if not unpaid
                else f"Meses pendientes: {', '.join(unpaid)}"
            ),
            "meses": enrollments,
        }
