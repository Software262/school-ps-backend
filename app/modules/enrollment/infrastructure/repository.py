from datetime import datetime

from sqlmodel import Session, col, func, or_, select

from app.modules.enrollment.domain.entities import (
    ComplementaryDetail,
    GradeInfo,
    StudentGeneralInfo,
    StudentInfo,
)
from app.modules.enrollment.domain.repositories import EnrollmentRepository
from app.modules.enrollment.infrastructure.models import (
    Acudiente,
    Complementario,
    DetalleMatricula,
    Estudiante,
    Grado,
    Matricula,
    Pago,
    PagoDetalle,
    ParametrizarMatricula,
)


class SQLEnrollmentRepository(EnrollmentRepository):
    """Implementación concreta del repositorio usando SQLModel/PostgreSQL."""

    def __init__(self, session: Session) -> None:
        self._session = session

    # === Consulta ===

    def get_student_by_id(self, student_id: int) -> StudentInfo | None:
        statement = (
            select(Estudiante, Grado)
            .join(Grado, col(Estudiante.grado_id) == col(Grado.id))
            .where(Estudiante.id == student_id)
        )
        result = self._session.exec(statement).first()
        if result is None:
            return None

        estudiante, grado = result
        assert estudiante.id is not None
        assert estudiante.grado_id is not None
        return StudentInfo(
            id=estudiante.id,
            nombre=estudiante.nombre,
            documento=estudiante.documento,
            grado_id=estudiante.grado_id,
            grado_nombre=grado.nombre,
            activo=estudiante.activo,
        )

    def get_enrollment_base_cost(self, grade_id: int, year: int) -> int | None:
        statement = select(ParametrizarMatricula).where(
            ParametrizarMatricula.grado_id == grade_id,
            ParametrizarMatricula.anio == year,
        )
        result = self._session.exec(statement).first()
        return result.valor if result else None

    def get_enrollment_details(
        self, student_id: int, year: int
    ) -> tuple[int | None, str, list[ComplementaryDetail], int, int]:
        # Buscar la matrícula del estudiante para el año dado
        statement = (
            select(Matricula)
            .join(
                ParametrizarMatricula,
                col(Matricula.para_matricula_id) == col(ParametrizarMatricula.id),
            )
            .where(
                Matricula.estudiante_id == student_id,
                ParametrizarMatricula.anio == year,
            )
        )
        matricula = self._session.exec(statement).first()

        if matricula is None:
            return None, "sin_abono", [], 0, 0

        # Obtener detalles con complementarios
        detail_statement = (
            select(DetalleMatricula, Complementario)
            .join(
                Complementario,
                col(DetalleMatricula.complementario_id) == col(Complementario.id),
            )
            .where(DetalleMatricula.matricula_id == matricula.id)
        )
        details = self._session.exec(detail_statement).all()

        complementary_items = [
            ComplementaryDetail(
                detalle_id=det.id if det.id is not None else 0,
                complementario_id=comp.id if comp.id is not None else 0,
                tipo_complementario=comp.tipo_complementario,
                valor=comp.valor,
                descuento=det.descuento,
                valor_completo=det.valor_completo,
                valor_pendiente=det.valor_pendiente,
            )
            for det, comp in details
        ]

        return (
            matricula.id,
            matricula.estado_matricula,
            complementary_items,
            matricula.valor_pendiente_base,
            matricula.valor_total,
        )

    # === Registro de matrícula ===

    def get_param_matricula_id(self, grade_id: int, year: int) -> int | None:
        statement = select(ParametrizarMatricula).where(
            ParametrizarMatricula.grado_id == grade_id,
            ParametrizarMatricula.anio == year,
        )
        result = self._session.exec(statement).first()
        return result.id if result else None

    def student_has_enrollment(self, student_id: int, year: int) -> bool:
        statement = (
            select(Matricula)
            .join(
                ParametrizarMatricula,
                col(Matricula.para_matricula_id) == col(ParametrizarMatricula.id),
            )
            .where(
                Matricula.estudiante_id == student_id,
                ParametrizarMatricula.anio == year,
            )
        )
        return self._session.exec(statement).first() is not None

    def get_active_complementaries(self, year: int) -> list[tuple[int, str, int]]:
        statement = select(Complementario).where(
            Complementario.anio == year,
            col(Complementario.uso_matricula),
            Complementario.estado_complemento == "Activo",
        )
        results = self._session.exec(statement).all()
        return [
            (comp.id, comp.tipo_complementario, comp.valor)
            for comp in results
            if comp.id is not None
        ]

    def create_enrollment(
        self,
        para_matricula_id: int,
        student_id: int,
        period_id: int,
        valor_total: int,
        base_cost: int,
        complementary_details: list[tuple[int, int]],
    ) -> tuple[int, list[int]]:
        matricula = Matricula(
            para_matricula_id=para_matricula_id,
            estudiante_id=student_id,
            periodo_id=period_id,
            valor_total=valor_total,
            fecha_registro=datetime.now(),
            estado_matricula="sin_abono",
            valor_pendiente_base=base_cost,
        )
        self._session.add(matricula)
        self._session.flush()

        assert matricula.id is not None

        detail_ids = []
        for comp_id, valor in complementary_details:
            detalle = DetalleMatricula(
                matricula_id=matricula.id,
                complementario_id=comp_id,
                cuota=1,
                descuento=0,
                valor_completo=valor,
                valor_pendiente=valor,
                fecha_abono=datetime.now(),
            )
            self._session.add(detalle)
            self._session.flush()
            if detalle.id is not None:
                detail_ids.append(detalle.id)

        self._session.commit()
        return matricula.id, detail_ids

    # === Pagos ===

    def get_enrollment_by_id(self, matricula_id: int) -> tuple | None:
        statement = select(Matricula).where(Matricula.id == matricula_id)
        mat = self._session.exec(statement).first()
        if mat is None:
            return None
        return (
            mat.id,
            mat.estudiante_id,
            mat.valor_total,
            mat.estado_matricula,
            mat.valor_pendiente_base,
            mat.para_matricula_id,
        )

    def get_enrollment_complementary_details(
        self, matricula_id: int
    ) -> list[tuple[int, int, str, int, int, int]]:
        statement = (
            select(DetalleMatricula, Complementario)
            .join(
                Complementario,
                col(DetalleMatricula.complementario_id) == col(Complementario.id),
            )
            .where(DetalleMatricula.matricula_id == matricula_id)
        )
        results = self._session.exec(statement).all()
        return [
            (
                det.id,
                comp.id,
                comp.tipo_complementario,
                det.valor_pendiente,
                det.valor_completo,
                det.descuento,
            )
            for det, comp in results
            if det.id is not None and comp.id is not None
        ]

    def validate_talonario_unique(self, codigo: str) -> bool:
        statement = select(Pago).where(Pago.codigo_talonario == codigo)
        return self._session.exec(statement).first() is None

    def create_payment(
        self,
        matricula_id: int,
        codigo_talonario: str,
        monto_total: int,
        observacion: str | None,
        distribuciones: list[tuple[str, int | None, int]],
    ) -> int:
        pago = Pago(
            matricula_id=matricula_id,
            codigo_talonario=codigo_talonario,
            monto_total=monto_total,
            fecha_pago=datetime.now(),
            observacion=observacion,
        )
        self._session.add(pago)
        self._session.flush()

        assert pago.id is not None

        for concepto, comp_id, monto in distribuciones:
            detalle = PagoDetalle(
                pago_id=pago.id,
                concepto=concepto,
                complementario_id=comp_id,
                monto_aplicado=monto,
            )
            self._session.add(detalle)

        self._session.commit()
        return pago.id

    def update_pending_base(self, matricula_id: int, new_pending: int) -> None:
        statement = select(Matricula).where(Matricula.id == matricula_id)
        mat = self._session.exec(statement).one()
        mat.valor_pendiente_base = new_pending
        self._session.add(mat)
        self._session.flush()

    def update_complementary_pending(
        self,
        matricula_id: int,
        complementario_id: int,
        new_pending: int,
        detalle_id: int | None = None,
    ) -> None:
        if detalle_id is not None:
            statement = select(DetalleMatricula).where(
                DetalleMatricula.id == detalle_id
            )
        else:
            statement = select(DetalleMatricula).where(
                DetalleMatricula.matricula_id == matricula_id,
                DetalleMatricula.complementario_id == complementario_id,
            )
        det = self._session.exec(statement).one()
        det.valor_pendiente = new_pending
        self._session.add(det)
        self._session.flush()

    def update_enrollment_status(self, matricula_id: int, status: str) -> None:
        statement = select(Matricula).where(Matricula.id == matricula_id)
        mat = self._session.exec(statement).one()
        mat.estado_matricula = status
        self._session.add(mat)
        self._session.commit()

    def enrollment_has_payments(self, matricula_id: int) -> bool:
        """Retorna True si existe al menos un pago registrado para esta matrícula."""
        statement = select(Pago).where(Pago.matricula_id == matricula_id)
        return self._session.exec(statement).first() is not None

    def update_enrollment_details(
        self,
        matricula_id: int,
        nuevo_valor_total: int,
        nuevo_base: int,
        comp_updates: list[tuple[int, int, int, int]],
    ) -> None:
        statement = select(Matricula).where(Matricula.id == matricula_id)
        matricula = self._session.exec(statement).first()
        if not matricula:
            return

        matricula.valor_total = nuevo_valor_total
        matricula.valor_pendiente_base = nuevo_base
        self._session.add(matricula)

        for det_id, nuevo_completo, nuevo_descuento, nuevo_comp_pending in comp_updates:
            det_statement = select(DetalleMatricula).where(
                DetalleMatricula.id == det_id
            )
            detalle = self._session.exec(det_statement).first()
            if detalle:
                detalle.valor_completo = nuevo_completo
                detalle.descuento = nuevo_descuento
                detalle.valor_pendiente = nuevo_comp_pending
                self._session.add(detalle)

        self._session.commit()

    # === Complementarios ===

    def create_complementary(
        self,
        tipo_complementario: str,
        anio: int,
        valor: int,
        estado: str,
        uso_matricula: bool,
    ) -> int:
        comp = Complementario(
            tipo_complementario=tipo_complementario,
            anio=anio,
            valor=valor,
            estado_complemento=estado,
            uso_matricula=uso_matricula,
        )
        self._session.add(comp)
        self._session.commit()
        assert comp.id is not None
        return comp.id

    def get_complementary_by_id(self, complementary_id: int) -> tuple[int, int] | None:
        statement = select(Complementario).where(Complementario.id == complementary_id)
        comp = self._session.exec(statement).first()
        if comp is None:
            return None
        assert comp.id is not None
        return (comp.id, comp.valor)

    def assign_complementary_to_enrollment(
        self,
        matricula_id: int,
        complementary_id: int,
        valor_completo: int,
        descuento: int,
    ) -> int:
        detalle = DetalleMatricula(
            matricula_id=matricula_id,
            complementario_id=complementary_id,
            cuota=1,
            descuento=descuento,
            valor_completo=valor_completo,
            valor_pendiente=valor_completo - descuento,
            fecha_abono=datetime.now(),
        )
        self._session.add(detalle)
        self._session.commit()
        assert detalle.id is not None
        return detalle.id

    def increase_enrollment_total_value(self, matricula_id: int, amount: int) -> None:
        statement = select(Matricula).where(Matricula.id == matricula_id)
        mat = self._session.exec(statement).first()
        if mat:
            mat.valor_total += amount
            self._session.add(mat)
            self._session.commit()

    # === Estudiantes ===

    def find_or_create_student(
        self,
        documento: str,
        nombre: str,
        grado_id: int,
        acudiente_id: int,
    ) -> int:
        statement = select(Estudiante).where(Estudiante.documento == documento)
        estudiante = self._session.exec(statement).first()

        if not estudiante:
            estudiante = Estudiante(
                documento=documento,
                nombre=nombre,
                grado_id=grado_id,
                acudiente_id=acudiente_id,
                activo=True,
                fecha_activo=datetime.now(),
            )
            self._session.add(estudiante)
            self._session.commit()
            self._session.refresh(estudiante)
        else:
            if (
                estudiante.grado_id != grado_id
                or estudiante.acudiente_id != acudiente_id
            ):
                estudiante.grado_id = grado_id
                estudiante.acudiente_id = acudiente_id
                self._session.add(estudiante)
                self._session.commit()

        assert estudiante.id is not None
        return estudiante.id

    def get_payments_count(self, matricula_id: int) -> int:
        statement = select(Pago).where(Pago.matricula_id == matricula_id)
        results = self._session.exec(statement).all()
        return len(results)

    def get_total_paid(self, matricula_id: int) -> int:
        statement = select(Pago).where(Pago.matricula_id == matricula_id)
        results = self._session.exec(statement).all()
        return sum(p.monto_total for p in results)

    def get_payments(self, matricula_id: int) -> list[Pago]:
        statement = select(Pago).where(Pago.matricula_id == matricula_id)
        return list(self._session.exec(statement).all())

    def search_students(
        self, documento: str | None, nombre: str | None
    ) -> list[tuple[Estudiante, Grado]]:
        statement = select(Estudiante, Grado).join(
            Grado,
            col(Estudiante.grado_id) == col(Grado.id),
        )
        if documento:
            doc_norm = documento.strip().lower()
            statement = statement.where(
                col(Estudiante.documento).ilike(f"%{doc_norm}%")
            )
        if nombre:
            nom_norm = nombre.strip().lower()
            statement = statement.where(col(Estudiante.nombre).ilike(f"%{nom_norm}%"))

        return list(self._session.exec(statement).all())

    def search_active_students(
        self, query: str | None, grado_id: int | None, limit: int, offset: int
    ) -> list[StudentGeneralInfo]:
        statement = (
            select(Estudiante, Grado)
            .join(
                Grado,
                col(Estudiante.grado_id) == col(Grado.id),
            )
            .where(col(Estudiante.activo))
        )

        if query:
            q_norm = f"%{query.strip().lower()}%"
            statement = statement.where(
                or_(
                    func.lower(Estudiante.nombre).like(q_norm),
                    func.lower(Estudiante.documento).like(q_norm),
                )
            )
        if grado_id is not None:
            statement = statement.where(col(Estudiante.grado_id) == grado_id)

        statement = statement.offset(offset).limit(limit)
        results = self._session.exec(statement).all()
        return [
            StudentGeneralInfo(
                id=est.id,
                nombre=est.nombre,
                documento=est.documento,
                grado_nombre=gr.nombre,
            )
            for est, gr in results
            if est.id is not None
        ]

    def get_students_bulk(self, student_ids: list[int]) -> list[StudentGeneralInfo]:
        statement = (
            select(Estudiante, Grado)
            .join(Grado, col(Estudiante.grado_id) == col(Grado.id))
            .where(col(Estudiante.id).in_(student_ids))
        )
        results = self._session.exec(statement).all()
        return [
            StudentGeneralInfo(
                id=est.id,
                nombre=est.nombre,
                documento=est.documento,
                grado_nombre=gr.nombre,
            )
            for est, gr in results
            if est.id is not None
        ]

    def get_all_grades(self) -> list[GradeInfo]:
        statement = select(Grado).order_by(col(Grado.nombre))
        results = self._session.exec(statement).all()
        return [
            GradeInfo(id=gr.id, nombre=gr.nombre)  # type: ignore
            for gr in results
            if gr.id is not None
        ]

    def get_student_entity_by_id(self, student_id: int) -> Estudiante | None:
        statement = select(Estudiante).where(col(Estudiante.id) == student_id)
        return self._session.exec(statement).first()

    def get_student_entities_by_grade(self, grado_id: int) -> list[Estudiante]:
        statement = select(Estudiante).where(col(Estudiante.grado_id) == grado_id)
        return list(self._session.exec(statement).all())

    def get_all_complementaries_by_year(self, year: int) -> list[Complementario]:
        statement = select(Complementario).where(
            col(Complementario.anio) == year,
            col(Complementario.estado_complemento) == "Activo",
        )
        return list(self._session.exec(statement).all())

    # === Nuevas Consultas y Acciones ===

    def get_grade_by_name(self, name: str) -> int | None:
        statement = select(Grado).where(col(Grado.nombre).ilike(name.strip()))
        grade = self._session.exec(statement).first()
        return grade.id if grade else None

    def get_acudiente_by_name(self, name: str) -> int | None:
        statement = select(Acudiente).where(col(Acudiente.nombre).ilike(name.strip()))
        acudiente = self._session.exec(statement).first()
        return acudiente.id if acudiente else None

    def create_acudiente(
        self, nombre: str, parentesco: str, telefono: str, correo: str
    ) -> int:
        acudiente = Acudiente(
            nombre=nombre.strip(),
            parentesco=parentesco.strip(),
            telefono=telefono.strip(),
            correo=correo.strip(),
        )
        self._session.add(acudiente)
        self._session.commit()
        assert acudiente.id is not None
        return acudiente.id

    def get_payments_by_matricula(self, matricula_id: int) -> list:
        statement = (
            select(Pago)
            .where(Pago.matricula_id == matricula_id)
            .order_by(col(Pago.fecha_pago).desc())
        )
        return list(self._session.exec(statement).all())

    def get_payment_by_id(self, pago_id: int) -> tuple | None:
        statement = select(Pago).where(Pago.id == pago_id)
        pago = self._session.exec(statement).first()
        if pago:
            return (
                pago.id,
                pago.matricula_id,
                pago.codigo_talonario,
                pago.monto_total,
                pago.fecha_pago,
                pago.observacion,
            )
        return None

    def get_payment_details(self, pago_id: int) -> list[tuple[str, int | None, int]]:
        statement = select(
            PagoDetalle.concepto,
            PagoDetalle.complementario_id,
            PagoDetalle.monto_aplicado,
        ).where(PagoDetalle.pago_id == pago_id)
        details = self._session.exec(statement).all()
        return [
            (
                str(concepto),
                int(comp_id) if comp_id is not None else None,
                int(monto),
            )
            for concepto, comp_id, monto in details
        ]

    def get_payment_receipt_data(
        self, pago_id: int
    ) -> tuple[Pago, Matricula, Estudiante, Grado, Acudiente] | None:
        statement = (
            select(Pago, Matricula, Estudiante, Grado)
            .join(Matricula, col(Pago.matricula_id) == col(Matricula.id))
            .join(Estudiante, col(Matricula.estudiante_id) == col(Estudiante.id))
            .join(Grado, col(Estudiante.grado_id) == col(Grado.id))
            .where(Pago.id == pago_id)
        )
        result = self._session.exec(statement).first()
        if result is None:
            return None

        pago, matricula, estudiante, grado = result

        acudiente_stmt = select(Acudiente).where(
            Acudiente.id == estudiante.acudiente_id
        )

        acudiente = self._session.exec(acudiente_stmt).first()

        if acudiente is None:
            return None

        return pago, matricula, estudiante, grado, acudiente

    def get_detalle_matricula(self, detalle_id: int) -> tuple | None:
        statement = select(DetalleMatricula).where(DetalleMatricula.id == detalle_id)
        det = self._session.exec(statement).first()
        if det is None:
            return None
        return (
            det.id,
            det.matricula_id,
            det.valor_completo,
            det.descuento,
            det.valor_pendiente,
        )

    def delete_detalle_matricula(self, detalle_id: int) -> None:
        statement = select(DetalleMatricula).where(DetalleMatricula.id == detalle_id)
        det = self._session.exec(statement).first()
        if det:
            self._session.delete(det)
            self._session.commit()

    def decrease_enrollment_total_value(self, matricula_id: int, amount: int) -> None:
        statement = select(Matricula).where(Matricula.id == matricula_id)
        mat = self._session.exec(statement).first()
        if mat:
            mat.valor_total -= amount
            self._session.add(mat)
            self._session.commit()
