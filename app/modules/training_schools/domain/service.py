from typing import Sequence
from app.modules.training_schools.domain.repositories import TrainingSchoolsRepository
from app.modules.training_schools.infrastructure.models import DetalleEscuelaFormacion
from app.modules.training_schools.schemas.request import (
    CreateEnrollmentRequest,
    RegisterPaymentRequest,
    UnsubscribeRequest,
)


class TrainingSchoolsService:
    def __init__(self, repository: TrainingSchoolsRepository):
        self.repository = repository

    async def enroll_student(self, data: CreateEnrollmentRequest) -> DetalleEscuelaFormacion | None:
        # Validate student existence
        student = await self.repository.get_student_by_id(data.estudiante_id)
        if not student:
            return None

        # Validate program existence
        program = await self.repository.get_complementario_by_id(data.complementario_id)
        if not program:
            return None

        # Validate program is active
        # The ERS mentions checking if program is active ("programa activo")
        if program.estado_complemento.lower() != "activo":
            return None

        # Validate no duplicate enrollment in same month
        existing = await self.repository.get_enrollment(
            student_id=data.estudiante_id,
            complementario_id=data.complementario_id,
            mes=data.mes
        )
        if existing:
            # Already enrolled
            return None

        # Create enrollment
        return await self.repository.create_enrollment(data)

    async def register_payment(self, data: RegisterPaymentRequest) -> DetalleEscuelaFormacion | None:
        # Retrieve the enrollment record
        enrollment = await self.repository.get_enrollment(
            student_id=data.estudiante_id,
            complementario_id=data.complementario_id,
            mes=data.mes
        )
        if not enrollment:
            return None

        # Check if already paid or inactive
        if not enrollment.activo:
            return None

        # Update payment status
        enrollment.estado_escuela = True
        return await self.repository.save_enrollment(enrollment)

    async def unsubscribe_student(
        self, student_id: int, complementario_id: int, mes: str, data: UnsubscribeRequest
    ) -> DetalleEscuelaFormacion | None:
        # Retrieve the enrollment record
        enrollment = await self.repository.get_enrollment(
            student_id=student_id,
            complementario_id=complementario_id,
            mes=mes
        )
        if not enrollment:
            return None

        # Mark as inactive and persist the unsubscribe reason
        enrollment.activo = False
        enrollment.motivo_baja = data.motivo
        return await self.repository.save_enrollment(enrollment)

    async def get_student_status(self, student_id: int) -> dict:
        student = await self.repository.get_student_by_id(student_id)
        if not student:
            return {
                "estudiante_id": student_id,
                "paz_y_salvo": False,
                "detalle": "El estudiante no existe."
            }

        enrollments = await self.repository.get_student_enrollments(student_id)
        
        # Filter active enrollments
        active_enrollments = [e for e in enrollments if e.activo]

        # If any active enrollment has estado_escuela = False (unpaid), they are blocked
        unpaid = []
        for e in active_enrollments:
            if not e.estado_escuela:
                # We can fetch the program name
                program = await self.repository.get_complementario_by_id(e.complementario_id)
                program_name = program.tipo_complementario if program else f"Programa #{e.complementario_id}"
                unpaid.append(f"{program_name} ({e.mes})")

        if unpaid:
            return {
                "estudiante_id": student_id,
                "paz_y_salvo": False,
                "detalle": f"Mensualidades pendientes en: {', '.join(unpaid)}"
            }

        return {
            "estudiante_id": student_id,
            "paz_y_salvo": True,
            "detalle": "Paz y salvo en todas las escuelas de formación activas."
        }

    async def list_student_enrollments(self, student_id: int) -> Sequence[DetalleEscuelaFormacion]:
        return await self.repository.get_student_enrollments(student_id)

    async def list_program_enrollments(self, complementario_id: int) -> Sequence[DetalleEscuelaFormacion]:
        return await self.repository.get_enrollments_by_program(complementario_id)
