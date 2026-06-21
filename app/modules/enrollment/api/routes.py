from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import col, select

from app.core.db import SessionDep
from app.modules.enrollment.application.assign_complementary import (
    AssignComplementary,
)
from app.modules.enrollment.application.create_complementary import (
    CreateComplementary,
)
from app.modules.enrollment.application.disassociate_complementary import (
    DisassociateComplementary,
)
from app.modules.enrollment.application.get_enrollment_balance import (
    GetEnrollmentBalance,
)
from app.modules.enrollment.application.get_payment_history import GetPaymentHistory
from app.modules.enrollment.application.get_payment_receipt import GetPaymentReceipt
from app.modules.enrollment.application.manual_enrollment import ManualEnrollment
from app.modules.enrollment.application.modify_enrollment import ModifyEnrollment
from app.modules.enrollment.application.process_payment import ProcessDirectedPayment
from app.modules.enrollment.application.register_enrollment import (
    RegisterEnrollment,
)
from app.modules.enrollment.application.get_all_grades import GetAllGrades
from app.modules.enrollment.application.get_all_periods import GetAllPeriods
from app.modules.enrollment.application.get_complementaries import GetComplementaries
from app.modules.enrollment.application.get_students_bulk import GetStudentsBulk
from app.modules.enrollment.application.search_active_students import (
    SearchActiveStudents,
)
from app.modules.enrollment.application.search_students import SearchStudents
from app.modules.enrollment.infrastructure.models import Estudiante, Grado
from app.modules.enrollment.schemas.request import (
    AssignComplementaryRequest,
    ComplementaryCreateRequest,
    DirectedPaymentRequest,
    ManualEnrollmentRequest,
    ModifyEnrollmentRequest,
    RegisterEnrollmentRequest,
)
from app.modules.enrollment.schemas.response import (
    AcudienteReceiptInfo,
    ComplementaryItemResponse,
    EnrollmentBalanceResponse,
    EnrollmentCreatedResponse,
    PaymentDistributionResponse,
    PaymentHistoryItemResponse,
    PaymentReceiptResponse,
    StudentBasicSearchItemResponse,
    StudentBasicSearchListResponse,
    ComplementaryConceptResponse,
    PaymentResultResponse,
    StudentInfoResponse,
    StudentReceiptInfo,
    StudentSearchItemResponse,
    StudentSearchListResponse,
    GradeResponse,
    StudentGeneralResponse,
    PeriodResponse,
)

router = APIRouter(
    responses={
        200: {"description": "OK"},
        404: {"description": "Recurso no encontrado"},
    },
)


@router.get(
    "/students/{student_id}/balance",
    response_model=EnrollmentBalanceResponse,
    summary="Obtener balance de matrícula de un estudiante",
    description=(
        "Retorna el desglose completo de lo que un estudiante debe en su "
        "matrícula, incluyendo el costo base, complementarios asignados "
        "y el primer mes de pensión."
    ),
)
async def get_enrollment_balance(
    session: SessionDep,
    student_id: int,
    year: int | None = Query(
        default=None,
        description="Año a consultar. Si no se envía, se usa el año actual.",
    ),
) -> EnrollmentBalanceResponse:
    if year is None:
        year = datetime.now().year

    use_case = GetEnrollmentBalance(session=session)

    try:
        balance = use_case.execute(student_id, year)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    return EnrollmentBalanceResponse(
        estudiante=StudentInfoResponse(
            id=balance.student.id,
            nombre=balance.student.nombre,
            documento=balance.student.documento,
            grado_id=balance.student.grado_id,
            grado_nombre=balance.student.grado_nombre,
            activo=balance.student.activo,
        ),
        anio=balance.year,
        costo_base_matricula=balance.enrollment_base_cost,
        complementarios=[
            ComplementaryItemResponse(
                detalle_id=item.detalle_id,
                complementario_id=item.complementario_id,
                tipo_complementario=item.tipo_complementario,
                valor=item.valor,
                descuento=item.descuento,
                valor_completo=item.valor_completo,
                valor_pendiente=item.valor_pendiente,
            )
            for item in balance.complementary_items
        ],
        total_complementarios=balance.complementary_total,
        costo_total=balance.total_cost,
        total_pagado=balance.total_paid,
        total_pendiente=balance.total_pending,
        estado_matricula=balance.enrollment_status,
        matricula_registrada=balance.enrollment_exists,
        pendiente_base=balance.pending_base,
        pagos_realizados=balance.payments_count,
        matricula_id=balance.matricula_id,
    )


@router.get(
    "/students/basic",
    response_model=StudentBasicSearchListResponse,
    summary="Buscar estudiantes con datos básicos",
    description=(
        "Retorna estudiantes por nombre o documento sin calcular balance de "
        "matrícula ni consultar complementarios."
    ),
)
async def search_students_basic(
    session: SessionDep,
    documento: str | None = Query(
        default=None,
        description="Coincidencia parcial del documento/código",
    ),
    nombre: str | None = Query(
        default=None,
        description="Coincidencia parcial del nombre",
    ),
    query: str | None = Query(
        default=None,
        description="Búsqueda unificada por documento/código o nombre",
    ),
    limit: int = Query(default=10, ge=1, le=50),
) -> StudentBasicSearchListResponse:
    statement = select(Estudiante, Grado).join(
        Grado, col(Estudiante.grado_id) == col(Grado.id)
    )

    if documento:
        statement = statement.where(col(Estudiante.documento).contains(documento))
    if nombre:
        statement = statement.where(col(Estudiante.nombre).ilike(f"%{nombre}%"))
    if query:
        statement = statement.where(
            col(Estudiante.documento).contains(query)
            | col(Estudiante.nombre).ilike(f"%{query}%")
        )

    rows = session.exec(
        statement.order_by(col(Estudiante.nombre)).limit(limit)
    ).all()
    items = [
        StudentBasicSearchItemResponse(
            id=student.id or 0,
            nombre=student.nombre,
            documento=student.documento,
            grado=grade.nombre,
            curso=None,
        )
        for student, grade in rows
    ]

    return StudentBasicSearchListResponse(
        estudiantes=items,
        total_resultados=len(items),
    )


@router.get(
    "/students",
    response_model=StudentSearchListResponse,
    summary="Buscar estudiantes con su estado de matrícula y balance",
    description="Retorna una lista de estudiantes que coinciden con los filtros, con su balance consolidado.",
)
async def search_students(
    session: SessionDep,
    documento: str | None = Query(
        default=None,
        description="Coincidencia parcial del documento/código",
    ),
    nombre: str | None = Query(
        default=None,
        description="Coincidencia parcial del nombre",
    ),
    year: int | None = Query(
        default=None,
        description="Año a consultar. Si no se envía, se usa el año actual.",
    ),
    query: str | None = Query(
        default=None,
        description="Búsqueda unificada por documento/código o nombre",
    ),
) -> StudentSearchListResponse:
    if year is None:
        year = datetime.now().year

    use_case = SearchStudents(session=session)
    balances = use_case.execute(documento, nombre, year, query)

    items = []
    for b in balances:
        items.append(
            StudentSearchItemResponse(
                estudiante_id=b.student.id,
                documento=b.student.documento,
                nombre=b.student.nombre,
                grado_id=b.student.grado_id,
                grado_nombre=b.student.grado_nombre,
                anio=b.year,
                matricula_registrada=b.enrollment_exists,
                estado_matricula=(
                    b.enrollment_status if b.enrollment_exists else "sin_matricula"
                ),
                pagos_realizados=b.payments_count,
                saldo_pendiente=b.total_pending,
                costo_total=b.total_cost,
                total_pagado=b.total_paid,
            )
        )

    return StudentSearchListResponse(
        estudiantes=items,
        total_resultados=len(items),
    )


@router.post(
    "/register",
    response_model=EnrollmentCreatedResponse,
    status_code=201,
    summary="Registrar matrícula para un estudiante",
    description=(
        "Genera automáticamente la matrícula para un estudiante. "
        "Calcula el costo base según su grado, asigna los complementarios "
        "activos del tipo Matricula, y suma el primer mes de pensión."
    ),
)
async def register_enrollment(
    session: SessionDep,
    request: RegisterEnrollmentRequest,
) -> EnrollmentCreatedResponse:
    use_case = RegisterEnrollment(session=session)

    try:
        result = use_case.execute(
            request.estudiante_id, request.periodo_id, request.anio
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return EnrollmentCreatedResponse(
        matricula_id=result.matricula_id,
        estudiante_id=result.estudiante_id,
        valor_total=result.valor_total,
        costo_base=result.costo_base,
        total_complementarios=result.total_complementarios,
        complementarios=[
            ComplementaryItemResponse(
                detalle_id=c.detalle_id,
                complementario_id=c.complementario_id,
                tipo_complementario=c.tipo_complementario,
                valor=c.valor,
                descuento=c.descuento,
                valor_completo=c.valor_completo,
                valor_pendiente=c.valor_pendiente,
            )
            for c in result.complementarios
        ],
        mensaje=(
            f"Matrícula registrada exitosamente. Total a pagar: ${result.valor_total:,}"
        ),
    )


@router.put(
    "/students/{matricula_id}/matricula",
    status_code=200,
    summary="Modificar matrícula en tiempo real",
    description=(
        "Permite al administrador sobrescribir o aplicar descuentos al costo base, "
        "pensión o complementarios de una matrícula en tiempo real."
    ),
)
async def modify_enrollment(
    session: SessionDep,
    matricula_id: int,
    request: ModifyEnrollmentRequest,
) -> dict:
    use_case = ModifyEnrollment(session=session)

    try:
        result = use_case.execute(matricula_id, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return result


@router.post(
    "/payments/directed",
    response_model=PaymentResultResponse,
    status_code=201,
    summary="Pago con asignación dirigida",
    description=(
        "Registra un pago donde el padre especifica exactamente cuánto "
        "va a cada concepto (matrícula base, complementarios específicos, "
        "pensión). Valida que no se pague más de lo pendiente por concepto. "
        "Requiere código de talonario físico."
    ),
)
async def directed_payment(
    session: SessionDep,
    request: DirectedPaymentRequest,
) -> PaymentResultResponse:
    use_case = ProcessDirectedPayment(session=session)

    asignaciones = [
        (a.concepto, a.complementario_id, a.detalle_id, a.monto)
        for a in request.asignaciones
    ]

    try:
        result = use_case.execute(
            request.matricula_id,
            asignaciones,
            request.codigo_talonario,
            request.observacion,
        )
    except ValueError as e:
        error_msg = str(e)
        if "talonario" in error_msg.lower():
            raise HTTPException(status_code=409, detail=error_msg) from e
        if "excede" in error_msg.lower():
            raise HTTPException(status_code=400, detail=error_msg) from e
        raise HTTPException(status_code=400, detail=error_msg) from e

    if result.matricula_pagada:
        mensaje = "Matrícula completamente pagada!"
    else:
        mensaje = (
            f"Pago dirigido registrado. Saldo pendiente: "
            f"${result.saldo_restante_matricula:,}"
        )

    return PaymentResultResponse(
        pago_id=result.pago_id,
        codigo_talonario=result.codigo_talonario,
        monto_total=result.monto_total,
        monto_aplicado=result.monto_aplicado,
        distribuciones=[
            PaymentDistributionResponse(
                concepto=d.concepto,
                complementario_id=d.complementario_id,
                monto_aplicado=d.monto_aplicado,
            )
            for d in result.distribuciones
        ],
        saldo_restante=result.saldo_restante_matricula,
        matricula_pagada=result.matricula_pagada,
        mensaje=mensaje,
    )


@router.post(
    "/complementary",
    status_code=201,
    summary="Crear un concepto complementario nuevo",
)
async def create_complementary(
    session: SessionDep,
    request: ComplementaryCreateRequest,
):
    use_case = CreateComplementary(session=session)
    comp_id = use_case.execute(
        nombre=request.nombre,
        tipo_complementario_id=request.tipo_complementario_id,
        anio=request.anio,
        valor=request.valor,
        estado=request.estado_complemento,
    )
    return {
        "mensaje": "Complementario creado exitosamente",
        "complementario_id": comp_id,
    }


@router.post(
    "/students/{student_id}/complementary/assign",
    status_code=201,
    summary="Asignar un complementario a una matrícula existente",
)
async def assign_complementary(
    session: SessionDep,
    student_id: int,
    request: AssignComplementaryRequest,
    year: int | None = Query(
        default=None,
        description="Año de la matrícula. Si no se envía, se usa el año actual.",
    ),
):
    if year is None:
        year = datetime.now().year

    # Obtener el balance para resolver la matricula_id activa del estudiante
    use_case_balance = GetEnrollmentBalance(session=session)
    try:
        balance = use_case_balance.execute(student_id, year)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    if not balance.enrollment_exists or balance.matricula_id is None:
        raise HTTPException(
            status_code=400,
            detail=f"El estudiante con ID {student_id} no tiene matrícula activa para el año {year}",
        )

    use_case = AssignComplementary(session=session)

    try:
        detalle_id = use_case.execute(
            matricula_id=balance.matricula_id,
            complementary_id=request.complementario_id,
            descuento=request.descuento,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {
        "mensaje": "Complementario asignado exitosamente a la matrícula",
        "detalle_id": detalle_id,
    }


@router.post(
    "/students/manual",
    status_code=201,
    summary="Registrar y matricular manualmente a un estudiante",
)
async def manual_enrollment(
    session: SessionDep,
    request: ManualEnrollmentRequest,
):
    use_case = ManualEnrollment(session=session)
    try:
        matricula_id = use_case.execute(
            documento=request.documento,
            nombre=request.nombre,
            grado_str=request.grado,
            nombre_acudiente=request.nombre_acudiente,
            periodo_id=request.periodo_id,
            anio=request.anio,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {
        "mensaje": "Estudiante matriculado manualmente de forma exitosa",
        "matricula_id": matricula_id,
    }


@router.get(
    "/students/{student_id}/payments",
    response_model=list[PaymentHistoryItemResponse],
    summary="Obtener el historial de pagos (auditoría) de un estudiante",
)
async def get_payment_history(
    session: SessionDep,
    student_id: int,
    year: int | None = Query(
        default=None,
        description="Año a consultar. Si no se envía, se usa el año actual.",
    ),
) -> list[PaymentHistoryItemResponse]:
    if year is None:
        year = datetime.now().year

    use_case = GetPaymentHistory(session=session)
    try:
        payments = use_case.execute(student_id, year)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    return [
        PaymentHistoryItemResponse(
            id=p.id,
            codigo_talonario=p.codigo_talonario,
            monto_total=p.monto_total,
            fecha_pago=p.fecha_pago,
            observacion=p.observacion,
        )
        for p in payments
    ]


@router.get(
    "/payments/{pago_id}/receipt",
    response_model=PaymentReceiptResponse,
    summary="Obtener los datos del comprobante de pago por ID",
)
async def get_payment_receipt(
    session: SessionDep,
    pago_id: int,
) -> PaymentReceiptResponse:
    use_case = GetPaymentReceipt(session=session)
    try:
        receipt_data = use_case.execute(pago_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    return PaymentReceiptResponse(
        pago_id=receipt_data.pago_id,
        codigo_talonario=receipt_data.codigo_talonario,
        monto_total=receipt_data.monto_total,
        fecha_pago=receipt_data.fecha_pago,
        observacion=receipt_data.observacion,
        estudiante=StudentReceiptInfo(
            id=receipt_data.estudiante_id,
            nombre=receipt_data.nombre_estudiante,
            documento=receipt_data.documento_estudiante,
            grado=receipt_data.grado_estudiante,
        ),
        acudiente=AcudienteReceiptInfo(
            nombre=receipt_data.nombre_acudiente,
        ),
        distribuciones=[
            PaymentDistributionResponse(
                concepto=d.concepto,
                monto_aplicado=d.monto_aplicado,
            )
            for d in receipt_data.distribuciones
        ],
    )


@router.delete(
    "/details/{detalle_id}",
    status_code=200,
    summary="Desvincular un concepto complementario de un estudiante",
    description=(
        "Permite eliminar un concepto complementario específico asignado a un estudiante "
        "siempre y cuando no tenga abonos registrados para ese concepto."
    ),
)
async def disassociate_complementary(
    session: SessionDep,
    detalle_id: int,
):
    use_case = DisassociateComplementary(session=session)
    try:
        matricula_id = use_case.execute(detalle_id=detalle_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {
        "mensaje": "Concepto complementario desvinculado exitosamente",
        "detalle_id": detalle_id,
        "matricula_id": matricula_id,
    }


@router.get(
    "/complementary",
    response_model=list[ComplementaryConceptResponse],
    summary="Listar todos los conceptos complementarios disponibles",
    description="Retorna una lista de todos los conceptos complementarios registrados en el sistema, opcionalmente filtrados por año.",
)
async def get_complementaries(
    session: SessionDep,
    year: int | None = Query(
        default=None,
        description="Año para filtrar los conceptos complementarios.",
    ),
) -> list[ComplementaryConceptResponse]:
    use_case = GetComplementaries(session=session)
    results = use_case.execute(year=year)
    return [
        ComplementaryConceptResponse(
            id=item.id,
            tipo_complementario=item.tipo_complementario,
            anio=item.anio,
            valor=item.valor,
            estado_complemento=item.estado_complemento,
        )
        for item in results
    ]


@router.get(
    "/students/active",
    response_model=list[StudentGeneralResponse],
    summary="Buscar estudiantes activos",
)
async def search_active_students(
    session: SessionDep,
    query: str | None = Query(
        default=None, description="Nombre o documento del estudiante"
    ),
    grado_id: int | None = Query(default=None, description="Filtrar por grado"),
    limit: int = Query(default=10, description="Límite de resultados"),
    offset: int = Query(default=0, description="Offset de paginación"),
) -> list[StudentGeneralResponse]:
    use_case = SearchActiveStudents(session=session)
    return use_case.execute(query=query, grado_id=grado_id, limit=limit, offset=offset)


@router.post(
    "/students/bulk",
    response_model=list[StudentGeneralResponse],
    summary="Obtener estudiantes por lote (Bulk)",
)
async def get_students_bulk(
    session: SessionDep,
    student_ids: list[int],
) -> list[StudentGeneralResponse]:
    use_case = GetStudentsBulk(session=session)
    return use_case.execute(student_ids)


@router.get(
    "/grades",
    response_model=list[GradeResponse],
    summary="Listar todos los grados académicos",
)
async def get_all_grades(
    session: SessionDep,
) -> list[GradeResponse]:
    use_case = GetAllGrades(session=session)
    return use_case.execute()


@router.get(
    "/periods",
    response_model=list[PeriodResponse],
    summary="Listar todos los periodos académicos",
)
async def get_all_periods(
    session: SessionDep,
) -> list[PeriodResponse]:
    use_case = GetAllPeriods(session=session)
    return use_case.execute()
