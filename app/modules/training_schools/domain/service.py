from datetime import datetime

from app.modules.training_schools.application.contracts import EnrollmentDataService
from app.modules.training_schools.domain.entities import (
    ComplementarioInfo,
    PeriodInfo,
    ProgramInfo,
    StudentInfo,
    TipoComplementarioInfo,
)
from app.modules.training_schools.domain.repositories import (
    TrainingSchoolRepositoryInterface,
)
from app.modules.training_schools.infrastructure.models import DetalleEscuelaFormacion


class TrainingSchoolService:
    def __init__(
        self,
        repository: TrainingSchoolRepositoryInterface,
        enrollment: EnrollmentDataService,
    ) -> None:
        self.repository = repository
        self.enrollment = enrollment

    async def get_programs(self) -> list[ProgramInfo]:
        return await self.enrollment.get_all_programs()

    async def search_students(self, query: str) -> list[StudentInfo]:
        if not query or len(query.strip()) < 2:
            raise ValueError("La búsqueda requiere al menos 2 caracteres.")
        return await self.enrollment.search_students(query.strip())

    async def get_periods(self) -> list[PeriodInfo]:
        return await self.enrollment.get_periods()

    async def get_enrollments(self, periodo_id: int) -> list[DetalleEscuelaFormacion]:
        return await self.repository.get_enrollments_by_period(periodo_id)

    async def get_enrollments_with_students(
        self, periodo_id: int
    ) -> list[tuple[DetalleEscuelaFormacion, StudentInfo]]:
        enrollments = await self.repository.get_enrollments_by_period(periodo_id)
        result = []
        students_cache: dict = {}
        for enr in enrollments:
            if enr.estudiante_id not in students_cache:
                students_cache[
                    enr.estudiante_id
                ] = await self.enrollment.get_student_by_id(enr.estudiante_id)
            student = students_cache[enr.estudiante_id]
            if student:
                result.append((enr, student))
        return result

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
        existing = await self.repository.get_enrollment_by_student_program_period(
            estudiante_id, complementario_id, periodo_id
        )
        if existing and existing.activo:
            raise ValueError(
                "El estudiante ya está inscrito activamente en este programa y período."
            )

        programs = await self.enrollment.get_all_programs()
        program = next((p for p in programs if p.id == complementario_id), None)
        if not program:
            raise ValueError("Programa no encontrado.")

        student = await self.enrollment.get_student_by_id(estudiante_id)
        if not student:
            raise ValueError("Estudiante no encontrado.")

        if not await self.repository.validate_user_exists(usuario_id):
            raise ValueError("Usuario no encontrado.")

        base_valor = program.valor if program.valor and program.valor > 0 else 0
        saldo_pendiente = valor_acordado if valor_acordado is not None else base_valor
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
        if enrollment.saldo_pendiente == 0:
            enrollment.estado_escuela = True

        return await self.repository.save(enrollment)

    async def withdraw_student(
        self,
        enrollment_id: int,
        motivo: str,
        usuario_id: int,
    ) -> DetalleEscuelaFormacion:
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
        enrollments = await self.repository.get_active_enrollments_by_student(
            estudiante_id
        )
        return all(e.estado_escuela for e in enrollments)

    # === Gestión de tipos de complementario ===

    async def list_tipos_complementario(self) -> list[TipoComplementarioInfo]:
        return await self.enrollment.list_tipos_complementario()

    async def create_tipo_complementario(
        self, nombre: str, sub_tipo_complementario: int | None
    ) -> TipoComplementarioInfo:
        if not nombre or len(nombre.strip()) < 2:
            raise ValueError(
                "El nombre del tipo de complementario debe tener al menos 2 caracteres."
            )
        nombre = nombre.strip()
        tipos = await self.enrollment.list_tipos_complementario()
        if any(tipo.nombre.lower() == nombre.lower() for tipo in tipos):
            raise ValueError(
                f"Ya existe un tipo de complementario con el nombre '{nombre}'."
            )
        if sub_tipo_complementario is not None:
            padre = await self.enrollment.get_tipo_complementario(
                sub_tipo_complementario
            )
            if not padre:
                raise ValueError("El tipo de complementario padre no existe.")
        return await self.enrollment.create_tipo_complementario(
            nombre=nombre, sub_tipo_complementario=sub_tipo_complementario
        )

    async def update_tipo_complementario(
        self,
        tipo_id: int,
        nombre: str | None,
        estado: bool | None,
        sub_tipo_complementario: int | None,
    ) -> TipoComplementarioInfo:
        existing = await self.enrollment.get_tipo_complementario(tipo_id)
        if not existing:
            raise ValueError("Tipo de complementario no encontrado.")
        if nombre is not None:
            if len(nombre.strip()) < 2:
                raise ValueError(
                    "El nombre del tipo de complementario debe tener al menos 2 caracteres."
                )
            nombre = nombre.strip()
            tipos = await self.enrollment.list_tipos_complementario()
            if any(
                tipo.id != tipo_id and tipo.nombre.lower() == nombre.lower()
                for tipo in tipos
            ):
                raise ValueError(
                    f"Ya existe un tipo de complementario con el nombre '{nombre}'."
                )
        if sub_tipo_complementario is not None:
            if sub_tipo_complementario == tipo_id:
                raise ValueError(
                    "Un tipo de complementario no puede ser su propio padre."
                )
            padre = await self.enrollment.get_tipo_complementario(
                sub_tipo_complementario
            )
            if not padre:
                raise ValueError("El tipo de complementario padre no existe.")
        return await self.enrollment.update_tipo_complementario(
            tipo_id=tipo_id,
            nombre=nombre.strip() if nombre is not None else None,
            estado=estado,
            sub_tipo_complementario=sub_tipo_complementario,
        )

    async def delete_tipo_complementario(self, tipo_id: int) -> None:
        existing = await self.enrollment.get_tipo_complementario(tipo_id)
        if not existing:
            raise ValueError("Tipo de complementario no encontrado.")
        if await self.enrollment.tipo_complementario_has_children_or_concepts(tipo_id):
            raise ValueError(
                "No se puede eliminar: el tipo tiene subtipos o conceptos asociados."
            )
        await self.enrollment.delete_tipo_complementario(tipo_id)

    # === Gestión de complementarios ===

    async def list_complementarios(self) -> list[ComplementarioInfo]:
        return await self.enrollment.list_complementarios()

    async def create_complementario(
        self,
        nombre: str,
        anio: int,
        valor: int,
        estado_complemento: str,
        tipo_complementario_id: int,
    ) -> ComplementarioInfo:
        if not nombre or len(nombre.strip()) < 2:
            raise ValueError("El nombre del complementario es obligatorio.")
        if valor < 0:
            raise ValueError("El valor del complementario no puede ser negativo.")
        tipo = await self.enrollment.get_tipo_complementario(tipo_complementario_id)
        if not tipo:
            raise ValueError("El tipo de complementario no existe.")
        return await self.enrollment.create_complementario(
            nombre=nombre.strip(),
            anio=anio,
            valor=valor,
            estado_complemento=estado_complemento,
            tipo_complementario_id=tipo_complementario_id,
        )

    async def update_complementario(
        self,
        complementario_id: int,
        nombre: str | None,
        anio: int | None,
        valor: int | None,
        estado_complemento: str | None,
        tipo_complementario_id: int | None,
    ) -> ComplementarioInfo:
        existing = await self.enrollment.get_complementario(complementario_id)
        if not existing:
            raise ValueError("Complementario no encontrado.")
        if nombre is not None and len(nombre.strip()) < 2:
            raise ValueError("El nombre del complementario es obligatorio.")
        if valor is not None and valor < 0:
            raise ValueError("El valor del complementario no puede ser negativo.")
        if tipo_complementario_id is not None:
            tipo = await self.enrollment.get_tipo_complementario(tipo_complementario_id)
            if not tipo:
                raise ValueError("El tipo de complementario no existe.")
        return await self.enrollment.update_complementario(
            complementario_id=complementario_id,
            nombre=nombre.strip() if nombre is not None else None,
            anio=anio,
            valor=valor,
            estado_complemento=estado_complemento,
            tipo_complementario_id=tipo_complementario_id,
        )

    async def delete_complementario(self, complementario_id: int) -> None:
        existing = await self.enrollment.get_complementario(complementario_id)
        if not existing:
            raise ValueError("Complementario no encontrado.")
        if await self.enrollment.complementario_has_references(complementario_id):
            raise ValueError(
                "No se puede eliminar: el complementario está en uso en "
                "matrículas o inscripciones."
            )
        await self.enrollment.delete_complementario(complementario_id)
