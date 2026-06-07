from datetime import datetime

from app.modules.training_schools.domain.entities import (
    PeriodInfo,
    ProgramInfo,
    StudentInfo,
)
from app.modules.training_schools.domain.repositories import (
    TrainingSchoolRepositoryInterface,
)
from app.modules.training_schools.infrastructure.models import DetalleEscuelaFormacion


class TrainingSchoolService:
    def __init__(self, repository: TrainingSchoolRepositoryInterface) -> None:
        self.repository = repository

    async def get_programs(self) -> list[ProgramInfo]:
        # read-only: programs (complementarios) and their price are configured in
        # the matrícula module; escuelas de formación consumes them as-is.
        return await self.repository.get_all_programs()

    async def search_students(self, query: str) -> list[StudentInfo]:
        if not query or len(query.strip()) < 2:
            raise ValueError("La búsqueda requiere al menos 2 caracteres.")
        return await self.repository.search_students(query.strip())

    async def get_periods(self) -> list[PeriodInfo]:
        return await self.repository.get_periods()

    async def get_enrollments(self, periodo_id: int) -> list[DetalleEscuelaFormacion]:
        return await self.repository.get_enrollments_by_period(periodo_id)

    async def get_enrollments_with_students(
        self, periodo_id: int
    ) -> list[tuple[DetalleEscuelaFormacion, StudentInfo]]:
        return await self.repository.get_enrollments_with_students(periodo_id)

    async def enroll_student(
        self,
        estudiante_id: int,
        complementario_id: int,
        periodo_id: int,
        mes: str,
        usuario_id: int,
        observaciones: str | None = None,
        valor_acordado: int | None = None,
        numero_comprobante: str | None = None,
    ) -> DetalleEscuelaFormacion:
        # ef-rf-02: block duplicate active enrollment in the same program and period
        existing = await self.repository.get_enrollment_by_student_program_period(
            estudiante_id, complementario_id, periodo_id
        )
        if existing and existing.activo:
            raise ValueError(
                "El estudiante ya está inscrito activamente en este programa y período."
            )

        programs = await self.repository.get_all_programs()
        program = next((p for p in programs if p.id == complementario_id), None)
        if not program:
            raise ValueError("Programa no encontrado.")

        student = await self.repository.get_student_by_id(estudiante_id)
        if not student:
            raise ValueError("Estudiante no encontrado.")

        if not await self.repository.validate_user_exists(usuario_id):
            raise ValueError("Usuario no encontrado.")

        # ef-rf-03: use valor_acordado if provided, otherwise fall back to program price
        base_valor = program.valor if program.valor and program.valor > 0 else 0
        saldo_pendiente = valor_acordado if valor_acordado is not None else base_valor
        # ef-rf-04: if there's a pending balance, paz y salvo is blocked
        estado_escuela = saldo_pendiente == 0

        enrollment = DetalleEscuelaFormacion(
            complementario_id=complementario_id,
            estudiante_id=estudiante_id,
            periodo_id=periodo_id,
            fecha_registro=datetime.now(),
            mes=mes,
            activo=True,
            estado_escuela=estado_escuela,
            saldo_pendiente=saldo_pendiente,
            usuario_id=usuario_id,
            observaciones=observaciones,
            valor_acordado=saldo_pendiente,
            numero_comprobante=numero_comprobante,
        )
        return await self.repository.save(enrollment)

    async def register_payment(
        self,
        enrollment_id: int,
        monto: int,
        usuario_id: int,
    ) -> DetalleEscuelaFormacion:
        enrollment = await self.repository.get_enrollment(enrollment_id)
        if not enrollment:
            raise ValueError("Inscripción no encontrada.")
        if not enrollment.activo:
            raise ValueError(
                "La inscripción está inactiva; no se pueden registrar pagos."
            )
        if monto <= 0:
            raise ValueError("El monto del pago debe ser mayor a cero.")
        if not await self.repository.validate_user_exists(usuario_id):
            raise ValueError("Usuario no encontrado.")
        if monto > enrollment.saldo_pendiente:
            raise ValueError(
                f"El monto ({monto}) supera el saldo pendiente ({enrollment.saldo_pendiente})."
            )

        enrollment.saldo_pendiente -= monto
        enrollment.usuario_id = usuario_id
        enrollment.updated_at = datetime.now()
        # ef-rf-04: fully paid → unblock paz y salvo
        if enrollment.saldo_pendiente == 0:
            enrollment.estado_escuela = True

        return await self.repository.save(enrollment)

    async def withdraw_student(
        self,
        enrollment_id: int,
        motivo: str,
        usuario_id: int,
    ) -> DetalleEscuelaFormacion:
        # ef-rf-05: withdrawal with traceability
        enrollment = await self.repository.get_enrollment(enrollment_id)
        if not enrollment:
            raise ValueError("Inscripción no encontrada.")
        if not enrollment.activo:
            raise ValueError("La inscripción ya está inactiva.")
        if not motivo or len(motivo.strip()) < 5:
            raise ValueError(
                "El motivo de retiro es obligatorio (mínimo 5 caracteres)."
            )
        if not await self.repository.validate_user_exists(usuario_id):
            raise ValueError("Usuario no encontrado.")

        enrollment.activo = False
        enrollment.motivo_retiro = motivo.strip()
        enrollment.usuario_id = usuario_id
        enrollment.updated_at = datetime.now()

        return await self.repository.save(enrollment)

    async def get_student_paz_y_salvo(self, estudiante_id: int) -> bool:
        # ef-rf-04: student loses paz y salvo if any active enrollment has pending balance
        enrollments = await self.repository.get_active_enrollments_by_student(
            estudiante_id
        )
        return all(e.estado_escuela for e in enrollments)
