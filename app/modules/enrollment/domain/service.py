from app.modules.enrollment.domain.entities import (
    ComplementaryDetail,
    EnrollmentBalance,
    EnrollmentCreated,
    PaymentAllocation,
    PaymentResult,
)
from app.modules.enrollment.domain.repositories import EnrollmentRepository

from app.modules.enrollment.schemas.request import ModifyEnrollmentRequest


class EnrollmentService:
    """Servicio de dominio que calcula el balance de matrícula."""

    def __init__(self, repository: EnrollmentRepository) -> None:
        self.repo = repository

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

        if enrollment_exists:
            # Usar valor_total real de la matrícula (se actualiza con descuentos)
            total_cost = valor_total
            total_pending = pending_base + sum(
                item.valor_pendiente for item in complementary_items
            )
        else:
            # Sin matrícula: usar costo parametrizado
            total_cost = base_cost + complementary_total
            total_pending = total_cost

        total_paid = total_cost - total_pending

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
        )

    def register_enrollment(
        self, student_id: int, period_id: int, year: int
    ) -> EnrollmentCreated:
        """
        Genera la matrícula automáticamente para un estudiante.

        1. Busca costo base por grado del estudiante
        2. Asigna complementarios activos con uso_matricula=True
        4. Crea registro Matricula + DetalleMatricula
        """
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
        }

    def process_directed_payment(
        self,
        matricula_id: int,
        asignaciones: list[tuple[str, int | None, int]],
        codigo_talonario: str,
        observacion: str | None = None,
    ) -> PaymentResult:
        """
        Procesa un pago con asignación dirigida.

        El usuario especifica exactamente cuánto va a cada concepto.
        Valida que no se pague más de lo pendiente por concepto.

        Args:
            asignaciones: Lista de (concepto, complementario_id, monto).
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
        comp_pending_map = {comp_id: pend for _, comp_id, _, pend, _, _ in comp_details}

        monto_total = 0
        distribuciones: list[PaymentAllocation] = []

        for concepto, comp_id, monto in asignaciones:
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
                current_pending = comp_pending_map.get(comp_id, 0)
                if monto > current_pending:
                    msg = (
                        f"Monto ${monto:,} excede el pendiente del "
                        f"complementario ID {comp_id} (${current_pending:,})"
                    )
                    raise ValueError(msg)
                new_pending = current_pending - monto
                self.repo.update_complementary_pending(
                    matricula_id, comp_id, new_pending
                )
                comp_pending_map[comp_id] = new_pending
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

        # Actualizar el estado semafórico de la matrícula (sin_abono / parcial / paz_y_salvo)
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

    def _update_enrollment_state(self, matricula_id: int) -> None:
        """Calcula y actualiza el estado semáfórico de la matrícula.

        Estados (MAT-RF-04 / MAT-RF-05):
        - 'sin_abono'  : Existe la obligación pero no hay ningún pago registrado.
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
            nuevo_estado = "sin_abono"

        self.repo.update_enrollment_status(matricula_id, nuevo_estado)

    def create_complementary(
        self,
        tipo_complementario: str,
        anio: int,
        valor: int,
        estado: str,
        uso_matricula: bool,
    ) -> int:
        return self.repo.create_complementary(
            tipo_complementario=tipo_complementario,
            anio=anio,
            valor=valor,
            estado=estado,
            uso_matricula=uso_matricula,
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
