from app.modules.enrollment.domain.entities import (
    ComplementaryDetail,
    EnrollmentBalance,
    EnrollmentCreated,
    PaymentAllocation,
    PaymentDistribution,
    PaymentHistoryItem,
    PaymentReceipt,
    PaymentResult,
    ComplementaryConcept,
    StudentInfo,
)
from app.modules.enrollment.domain.repositories import EnrollmentRepository
from app.modules.enrollment.application.contracts import TuitionServiceContract
from app.modules.enrollment.schemas.request import ModifyEnrollmentRequest
from app.modules.enrollment.schemas.response import (
    GradeResponse,
    StudentGeneralResponse,
    StudentResponse,
)


class EnrollmentService:
    """Servicio de dominio que calcula el balance de matrícula."""

    def __init__(
        self,
        repository: EnrollmentRepository,
        tuition_service: TuitionServiceContract | None = None,
    ) -> None:
        self.repo = repository
        self.tuition_service = tuition_service

    def get_balance(self, student_id: int, year: int) -> EnrollmentBalance:
        """
        Calcula el balance completo de matrícula de un estudiante.

        Incluye:
        - Costo base de matrícula (según grado y año)
        - Complementarios asignados (con descuentos)
        - Totales: costo, pagado y pendiente
        """
        student = self.repo.get_student_by_id(student_id)
        if student is None:
            msg = f"Estudiante con id {student_id} no encontrado"
            raise ValueError(msg)

        # Costo base de matrícula según grado y año (referencia parametrizada)
        base_cost = self.repo.get_enrollment_base_cost(student.grado_id, year) or 0

        # Detalles de matrícula (complementarios asignados)
        (
            matricula_id,
            enrollment_status,
            complementary_items,
            pending_base,
            valor_total,
        ) = self.repo.get_enrollment_details(student_id, year)
        enrollment_exists = matricula_id is not None

        complementary_total = sum(item.valor_completo for item in complementary_items)
        payments_count = 0
        total_paid = 0

        if enrollment_exists:
            if matricula_id is None:
                raise ValueError(
                    "El id de la matrícula no puede ser nulo cuando existe"
                )
            base_paid = self.repo.get_base_paid_amount(matricula_id)
            base_cost = pending_base + base_paid

            total_pending = pending_base + sum(
                item.valor_pendiente for item in complementary_items
            )
            payments_count = self.repo.get_payments_count(matricula_id)
            payments = self.repo.get_payments(matricula_id)
            total_paid = sum(p.monto_total for p in payments)
            total_cost = total_pending + total_paid
        else:
            # Sin matrícula: usar costo parametrizado
            total_cost = base_cost + complementary_total
            total_pending = total_cost
            total_paid = 0

        return EnrollmentBalance(
            student=student,
            year=year,
            enrollment_base_cost=base_cost,
            complementary_items=complementary_items,
            complementary_total=complementary_total,
            total_cost=total_cost,
            total_paid=total_paid,
            total_pending=total_pending,
            enrollment_status=enrollment_status,
            enrollment_exists=enrollment_exists,
            pending_base=pending_base,
            payments_count=payments_count,
            matricula_id=matricula_id,
        )

    def register_enrollment(
        self, student_id: int, period_id: int | None, year: int
    ) -> EnrollmentCreated:
        """
        Genera la matrícula automáticamente para un estudiante.

        1. Busca costo base por grado del estudiante
        2. Asigna complementarios activos del tipo Matricula
        4. Crea registro Matricula + DetalleMatricula
        """
        if period_id is None:
            period_id = self.repo.find_active_period_by_year(year)
            if period_id is None:
                msg = f"No se encontró un período académico activo para el año {year}"
                raise ValueError(msg)
        else:
            if not self.repo.period_exists(period_id):
                msg = f"El período académico con ID {period_id} no existe en el sistema"
                raise ValueError(msg)

        student = self.repo.get_student_by_id(student_id)
        if student is None:
            msg = f"Estudiante con id {student_id} no encontrado"
            raise ValueError(msg)

        if self.repo.student_has_enrollment(student_id, year):
            msg = (
                f"El estudiante {student_id} ya tiene matrícula registrada para {year}"
            )
            raise ValueError(msg)

        # Costo base
        base_cost = self.repo.get_enrollment_base_cost(student.grado_id, year)
        if base_cost is None:
            msg = (
                f"No hay costo de matrícula parametrizado para "
                f"grado '{student.grado_nombre}' en {year}"
            )
            raise ValueError(msg)

        param_id = self.repo.get_param_matricula_id(student.grado_id, year)
        if param_id is None:
            msg = "No se encontró parametrización de matrícula"
            raise ValueError(msg)

        # Complementarios activos
        active_comps = self.repo.get_active_complementaries(year)
        comp_details: list[tuple[int, int]] = []
        comp_entities: list[ComplementaryDetail] = []

        for comp_id, tipo, valor in active_comps:
            comp_details.append((comp_id, valor))
            comp_entities.append(
                ComplementaryDetail(
                    complementario_id=comp_id,
                    tipo_complementario=tipo,
                    valor=valor,
                    descuento=0,
                    valor_completo=valor,
                    valor_pendiente=valor,
                )
            )

        total_complementarios = sum(v for _, v in comp_details)

        valor_total = base_cost + total_complementarios

        # Crear en BD
        matricula_id, detail_ids = self.repo.create_enrollment(
            para_matricula_id=param_id,
            student_id=student_id,
            period_id=period_id,
            valor_total=valor_total,
            base_cost=base_cost,
            complementary_details=comp_details,
        )

        # Auto-create Pension record via tuition service
        if self.tuition_service is not None:
            self.tuition_service.create_pension_account(
                student_id=student_id,
                grade_id=student.grado_id,
                year=year,
            )

        for entity, d_id in zip(comp_entities, detail_ids):
            entity.detalle_id = d_id

        return EnrollmentCreated(
            matricula_id=matricula_id,
            estudiante_id=student_id,
            valor_total=valor_total,
            costo_base=base_cost,
            total_complementarios=total_complementarios,
            complementarios=comp_entities,
        )

    def modify_enrollment(
        self, matricula_id: int, request: "ModifyEnrollmentRequest"
    ) -> dict:
        """
        Modifica los costos y descuentos de la matrícula y recalcula el total.
        """
        enrollment = self.repo.get_enrollment_by_id(matricula_id)
        if enrollment is None:
            msg = f"Matrícula con id {matricula_id} no encontrada"
            raise ValueError(msg)

        (
            _mat_id,
            _est_id,
            valor_total_actual,
            _estado,
            pending_base,
            _param_id,
        ) = enrollment

        delta_total = 0

        nuevo_base = pending_base
        if request.nuevo_costo_base is not None:
            delta_total += request.nuevo_costo_base - pending_base
            nuevo_base = request.nuevo_costo_base
        elif request.descuento_base is not None:
            if request.descuento_base > pending_base:
                raise ValueError(
                    f"El descuento de base (${request.descuento_base:,}) no puede ser mayor "
                    f"al costo base pendiente (${pending_base:,})"
                )
            delta_total -= request.descuento_base
            nuevo_base -= request.descuento_base

        comp_details = self.repo.get_enrollment_complementary_details(matricula_id)
        comp_updates = []
        if request.complementarios:
            for mod in request.complementarios:
                detalle = next(
                    (d for d in comp_details if d[0] == mod.detalle_id), None
                )
                if not detalle:
                    msg = (
                        f"El detalle_id {mod.detalle_id} no pertenece a esta matrícula. "
                        f"Consulta el GET para obtener los detalle_id válidos."
                    )
                    raise ValueError(msg)

                det_id, comp_id, tipo, comp_pending, comp_completo, comp_descuento = (
                    detalle
                )

                nuevo_comp_pending = comp_pending
                nuevo_descuento = comp_descuento
                nuevo_completo = comp_completo

                if mod.nuevo_valor_completo is not None:
                    delta = mod.nuevo_valor_completo - comp_pending
                    delta_total += delta
                    nuevo_comp_pending = mod.nuevo_valor_completo
                    nuevo_completo = mod.nuevo_valor_completo
                elif mod.descuento is not None:
                    if mod.descuento > comp_pending:
                        raise ValueError(
                            f"El descuento (${mod.descuento:,}) no puede ser mayor "
                            f"al valor pendiente del complementario (${comp_pending:,})"
                        )
                    delta_total -= mod.descuento
                    nuevo_comp_pending -= mod.descuento
                    nuevo_descuento = mod.descuento

                comp_updates.append(
                    (det_id, nuevo_completo, nuevo_descuento, nuevo_comp_pending)
                )

        nuevo_valor_total = valor_total_actual + delta_total

        self.repo.update_enrollment_details(
            matricula_id, nuevo_valor_total, nuevo_base, comp_updates
        )

        self._update_enrollment_state(matricula_id)

        return {
            "mensaje": "Matrícula modificada exitosamente",
            "matricula_id": matricula_id,
            "nuevo_valor_total": nuevo_valor_total,
            "motivo_registrado": request.motivo,
            "observaciones_registradas": request.observaciones,
        }

    def process_directed_payment(
        self,
        matricula_id: int,
        asignaciones: list[tuple[str, int | None, int | None, int]],
        codigo_talonario: str,
        observacion: str | None = None,
    ) -> PaymentResult:
        """
        Procesa un pago con asignación dirigida.

        El usuario especifica exactamente cuánto va a cada concepto.
        Valida que no se pague más de lo pendiente por concepto.

        Args:
            asignaciones: Lista de (concepto, complementario_id, detalle_id, monto).
        """
        enrollment = self.repo.get_enrollment_by_id(matricula_id)
        if enrollment is None:
            msg = f"Matrícula con id {matricula_id} no encontrada"
            raise ValueError(msg)

        if not self.repo.validate_talonario_unique(codigo_talonario):
            msg = f"El código de talonario '{codigo_talonario}' ya está registrado"
            raise ValueError(msg)

        # Fix 3: Bloquear pago si la matrícula ya está completamente pagada
        saldo_actual = self._calculate_total_pending(matricula_id)
        if saldo_actual == 0:
            raise ValueError(
                "La matrícula ya está completamente pagada (saldo = $0). "
                "No se puede registrar un nuevo abono ordinario."
            )

        (
            _mat_id,
            _est_id,
            _valor_total,
            _estado,
            pending_base,
            _param_id,
        ) = enrollment

        comp_details = self.repo.get_enrollment_complementary_details(matricula_id)
        comp_pending_map = {det_id: pend for det_id, _, _, pend, _, _ in comp_details}

        monto_total = 0
        distribuciones: list[PaymentAllocation] = []

        for concepto, comp_id, detalle_id, monto in asignaciones:
            if monto <= 0:
                msg = f"El monto para '{concepto}' debe ser mayor a 0"
                raise ValueError(msg)

            if concepto == "matricula_base":
                if monto > pending_base:
                    msg = (
                        f"Monto ${monto:,} excede el pendiente de matrícula base "
                        f"(${pending_base:,})"
                    )
                    raise ValueError(msg)
                new_pending = pending_base - monto
                self.repo.update_pending_base(matricula_id, new_pending)
                pending_base = new_pending

            elif concepto.startswith("complementario") and comp_id is not None:
                target_det_id = detalle_id
                if target_det_id is None:
                    matching_details = [
                        det_id
                        for det_id, c_id, _, _, _, _ in comp_details
                        if c_id == comp_id and comp_pending_map.get(det_id, 0) > 0
                    ]
                    if matching_details:
                        target_det_id = matching_details[0]
                    else:
                        matching_details = [
                            det_id
                            for det_id, c_id, _, _, _, _ in comp_details
                            if c_id == comp_id
                        ]
                        if matching_details:
                            target_det_id = matching_details[0]

                if target_det_id is None:
                    msg = (
                        f"No se encontró asignación para el complementario ID {comp_id}"
                    )
                    raise ValueError(msg)

                current_pending = comp_pending_map.get(target_det_id, 0)
                if monto > current_pending:
                    msg = (
                        f"Monto ${monto:,} excede el pendiente del "
                        f"complementario ID {comp_id} (detalle ID {target_det_id}): ${current_pending:,}"
                    )
                    raise ValueError(msg)
                new_pending = current_pending - monto
                self.repo.update_complementary_pending(
                    matricula_id, comp_id, new_pending, target_det_id
                )
                comp_pending_map[target_det_id] = new_pending
            else:
                msg = f"Concepto '{concepto}' no reconocido"
                raise ValueError(msg)

            distribuciones.append(
                PaymentAllocation(
                    concepto=concepto,
                    complementario_id=comp_id,
                    monto_aplicado=monto,
                )
            )
            monto_total += monto

        # Registrar pago
        pago_id = self.repo.create_payment(
            matricula_id=matricula_id,
            codigo_talonario=codigo_talonario,
            monto_total=monto_total,
            observacion=observacion,
            distribuciones=[
                (d.concepto, d.complementario_id, d.monto_aplicado)
                for d in distribuciones
            ],
        )

        # Actualizar el estado semafórico de la matrícula (pendiente / parcial / paz_y_salvo)
        self._update_enrollment_state(matricula_id)
        saldo = self._calculate_total_pending(matricula_id)

        return PaymentResult(
            pago_id=pago_id,
            codigo_talonario=codigo_talonario,
            monto_total=monto_total,
            monto_aplicado=monto_total,
            distribuciones=distribuciones,
            saldo_restante_matricula=saldo,
            matricula_pagada=saldo == 0,
        )

    def _calculate_total_pending(self, matricula_id: int) -> int:
        """Calcula el total pendiente recargando datos frescos de la BD."""
        enrollment = self.repo.get_enrollment_by_id(matricula_id)
        if enrollment is None:
            return 0

        _, _, _, _, pending_base, _ = enrollment
        comp_details = self.repo.get_enrollment_complementary_details(matricula_id)
        comp_pending = sum(pend for _, _, _, pend, _, _ in comp_details)

        return pending_base + comp_pending

    def assign_complementary(
        self, matricula_id: int, complementary_id: int, descuento: int
    ) -> int:
        enrollment = self.repo.get_enrollment_by_id(matricula_id)
        if enrollment is None:
            raise ValueError(f"Matrícula con id {matricula_id} no encontrada")

        comp_data = self.repo.get_complementary_by_id(complementary_id)
        if comp_data is None:
            raise ValueError(f"Complementario con id {complementary_id} no encontrado")

        _, valor_completo = comp_data

        if descuento > valor_completo:
            raise ValueError(
                "El descuento no puede ser mayor al valor del complementario"
            )

        detalle_id = self.repo.assign_complementary_to_enrollment(
            matricula_id, complementary_id, valor_completo, descuento
        )

        monto_a_sumar = valor_completo - descuento
        self.repo.increase_enrollment_total_value(matricula_id, monto_a_sumar)
        self._update_enrollment_state(matricula_id)

        return detalle_id

    def disassociate_complementary(self, detalle_id: int) -> int:
        """
        Desvincula un concepto complementario de la matrícula de un estudiante.

        Valida que no existan abonos (pagos) aplicados al concepto.
        Si es válido, elimina el detalle, decrementa el valor_total de la matrícula y
        actualiza el estado de la matrícula.

        Returns:
            matricula_id de la matrícula afectada.
        """
        detalle = self.repo.get_detalle_matricula(detalle_id)
        if detalle is None:
            raise ValueError("Detalle de matrícula no encontrado")

        det_id, matricula_id, valor_completo, descuento, valor_pendiente = detalle

        # Validar que no se hayan registrado pagos (abonos) para este concepto
        valor_neto = valor_completo - descuento
        if valor_pendiente != valor_neto:
            raise ValueError(
                "No se puede desvincular un concepto que ya tiene abonos registrados"
            )

        # Eliminar el detalle de matrícula
        self.repo.delete_detalle_matricula(detalle_id)

        # Decrementar el valor total de la matrícula
        self.repo.decrease_enrollment_total_value(matricula_id, valor_neto)

        # Recalcular el estado de la matrícula (semafórico)
        self._update_enrollment_state(matricula_id)

        return matricula_id

    def _update_enrollment_state(self, matricula_id: int) -> None:
        """Calcula y actualiza el estado semáfórico de la matrícula.

        Estados (MAT-RF-04 / MAT-RF-05):
        - 'pendiente'  : Existe la obligación pero no hay ningún pago registrado.
        - 'parcial'    : Hay abonos registrados pero queda saldo mayor a cero.
        - 'paz_y_salvo': El saldo llegó a cero.
        """
        saldo = self._calculate_total_pending(matricula_id)
        tiene_pagos = self.repo.enrollment_has_payments(matricula_id)

        if saldo == 0:
            nuevo_estado = "paz_y_salvo"
        elif tiene_pagos:
            nuevo_estado = "parcial"
        else:
            nuevo_estado = "pendiente"

        self.repo.update_enrollment_status(matricula_id, nuevo_estado)

    def create_complementary(
        self,
        nombre: str,
        tipo_complementario_id: int | None,
        anio: int,
        valor: int,
        estado: str,
    ) -> int:
        if tipo_complementario_id is None:
            tipo_complementario_id = self.repo.get_or_create_matricula_tipo_id()
        return self.repo.create_complementary(
            nombre=nombre,
            tipo_complementario_id=tipo_complementario_id,
            anio=anio,
            valor=valor,
            estado=estado,
        )

    def find_or_create_student(
        self,
        documento: str,
        nombre: str,
        grado_id: int,
        acudiente_id: int,
    ) -> int:
        return self.repo.find_or_create_student(
            documento=documento,
            nombre=nombre,
            grado_id=grado_id,
            acudiente_id=acudiente_id,
        )

    def resolve_grade_id(self, grado_str: str) -> int:
        grado_str = grado_str.strip()
        try:
            val = int(grado_str)
            return val
        except ValueError:
            val_id = self.repo.get_grade_by_name(grado_str)
            if val_id is None:
                raise ValueError(f"El grado '{grado_str}' no existe")
            return val_id

    def resolve_or_create_acudiente(self, acudiente_str: str) -> int:
        acudiente_str = acudiente_str.strip()
        try:
            val = int(acudiente_str)
            return val
        except ValueError:
            ac_id = self.repo.get_acudiente_by_name(acudiente_str)
            if ac_id is None:
                ac_id = self.repo.create_acudiente(
                    nombre=acudiente_str,
                    parentesco="Representante",
                    telefono="No registrado",
                    correo="no_registrado@correo.com",
                )
            return ac_id

    def manual_enrollment(
        self,
        documento: str,
        nombre: str,
        grado_str: str,
        nombre_acudiente: str,
        period_id: int | None,
        year: int,
    ) -> int:
        grado_id = self.resolve_grade_id(grado_str)
        acudiente_id = self.resolve_or_create_acudiente(nombre_acudiente)

        student_id = self.repo.find_or_create_student(
            documento=documento.strip(),
            nombre=nombre.strip(),
            grado_id=grado_id,
            acudiente_id=acudiente_id,
        )

        result = self.register_enrollment(
            student_id=student_id,
            period_id=period_id,
            year=year,
        )
        return result.matricula_id

    def get_all_complementaries(
        self, year: int | None = None
    ) -> list[ComplementaryConcept]:
        """Obtiene todos los conceptos complementarios registrados."""
        return self.repo.get_all_complementaries(year=year)

    def search_students(
        self,
        documento: str | None,
        nombre: str | None,
        query: str | None = None,
    ) -> list[StudentInfo]:
        """Busca estudiantes y mapea los resultados crudos a entidades StudentInfo."""
        raw_results = self.repo.search_students(documento, nombre, query)
        students = []
        for est, gra in raw_results:
            if est.id is None or est.grado_id is None:
                continue
            students.append(
                StudentInfo(
                    id=est.id,
                    nombre=est.nombre,
                    documento=est.documento,
                    grado_id=est.grado_id,
                    grado_nombre=gra.nombre,
                    activo=est.activo,
                )
            )
        return students

    def search_students_with_balances(
        self,
        documento: str | None,
        nombre: str | None,
        year: int,
        query: str | None = None,
    ) -> list[EnrollmentBalance]:
        """Busca estudiantes y obtiene su balance consolidado en la capa de servicio."""
        students = self.search_students(documento, nombre, query)
        balances = []
        for student in students:
            balance = self.get_balance(student.id, year)
            balances.append(balance)
        return balances

    def get_payment_history(
        self, student_id: int, year: int
    ) -> list[PaymentHistoryItem]:
        student = self.repo.get_student_by_id(student_id)
        if student is None:
            raise ValueError(f"Estudiante con ID {student_id} no encontrado")

        matricula_id, _, _, _, _ = self.repo.get_enrollment_details(student_id, year)
        if matricula_id is None:
            return []

        pagos = self.repo.get_payments_by_matricula(matricula_id)
        return [
            PaymentHistoryItem(
                id=p.id,
                fecha_pago=p.fecha_pago,
                codigo_talonario=p.codigo_talonario,
                monto_total=p.monto_total,
                observacion=p.observacion,
            )
            for p in pagos
            if p.id is not None
        ]

    def get_payment_receipt(self, pago_id: int) -> PaymentReceipt:
        raw = self.repo.get_payment_receipt_data(pago_id)
        if raw is None:
            raise ValueError(f"Pago con ID {pago_id} no encontrado")

        pago, _matricula, estudiante, grado, acudiente = raw

        detalles = self.repo.get_payment_details(pago_id)
        distribuciones = [
            PaymentDistribution(
                concepto=concepto,
                monto_aplicado=monto,
            )
            for concepto, _comp_id, monto in detalles
        ]

        return PaymentReceipt(
            pago_id=pago_id,
            codigo_talonario=pago.codigo_talonario,
            fecha_pago=pago.fecha_pago,
            monto_total=pago.monto_total,
            observacion=pago.observacion,
            estudiante_id=estudiante.id,
            nombre_estudiante=estudiante.nombre,
            documento_estudiante=estudiante.documento,
            grado_estudiante=grado.nombre,
            nombre_acudiente=acudiente.nombre,
            distribuciones=distribuciones,
        )


class StudentService:
    """Servicio de dominio para consultas generales de estudiantes y grados."""

    def __init__(self, repository: EnrollmentRepository) -> None:
        self.repo = repository

    def search_active_students(
        self,
        query: str | None = None,
        grado_id: int | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[StudentGeneralResponse]:
        """Servicio 1: Búsqueda general de estudiantes activos."""
        students = self.repo.search_active_students(
            query=query, grado_id=grado_id, limit=limit, offset=offset
        )

        return [
            StudentGeneralResponse(
                id=p.id,
                nombre=p.nombre,
                documento=p.documento,
                grado_nombre=p.grado_nombre,
            )
            for p in students
            if p.id is not None
        ]

    def get_students_bulk(self, student_ids: list[int]) -> list[StudentGeneralResponse]:
        """Servicio 2: Información de estudiantes por lote (Bulk)."""
        if not student_ids:
            return []

        students = self.repo.get_students_bulk(student_ids)

        return [
            StudentGeneralResponse(
                id=p.id,
                nombre=p.nombre,
                documento=p.documento,
                grado_nombre=p.grado_nombre,
            )
            for p in students
            if p.id is not None
        ]

    def get_all_grades(self) -> list[GradeResponse]:
        """Servicio 3: Listado de grados disponibles en el sistema."""
        grades = self.repo.get_all_grades()

        return [GradeResponse(id=g.id, nombre=g.nombre) for g in grades]

    def get_student_by_id(self, student_id: int) -> StudentResponse | None:
        """Servicio 4: Obtiene el objeto/entidad Estudiante crudo por ID."""
        student = self.repo.get_student_entity_by_id(student_id)

        return (
            StudentResponse(
                nombre=student.nombre,
                activo=student.activo,
                acudiente_id=student.acudiente_id,
                documento=student.documento,
                fecha_activo=student.fecha_activo,
                grado_id=student.grado_id,
            )
            if student is not None
            else None
        )

    def get_students_by_grade(self, grado_id: int) -> list[StudentResponse]:
        """Servicio 5: Obtiene la lista de entidades Estudiante crudas en un grado."""
        students = self.repo.get_student_entities_by_grade(grado_id)

        return [
            StudentResponse(
                nombre=p.nombre,
                activo=p.activo,
                acudiente_id=p.acudiente_id,
                documento=p.documento,
                fecha_activo=p.fecha_activo,
                grado_id=p.grado_id,
            )
            for p in students
            if p.id is not None
        ]
