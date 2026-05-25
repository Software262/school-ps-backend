from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, UploadFile, File

from app.core.db import SessionDep
from app.modules.enrollment.application.assign_complementary import (
    AssignComplementary,
)
from app.modules.enrollment.application.create_complementary import (
    CreateComplementary,
)
from app.modules.enrollment.application.get_enrollment_balance import (
    GetEnrollmentBalance,
)
from app.modules.enrollment.application.mass_enrollment import MassEnrollment
from app.modules.enrollment.application.modify_enrollment import ModifyEnrollment
from app.modules.enrollment.application.process_payment import ProcessDirectedPayment
from app.modules.enrollment.application.register_enrollment import (
    RegisterEnrollment,
)
from app.modules.enrollment.schemas.request import (
    DirectedPaymentRequest,
    RegisterEnrollmentRequest,
    ModifyEnrollmentRequest,
    ComplementaryCreateRequest,
    AssignComplementaryRequest,
)
from app.modules.enrollment.schemas.response import (
    ComplementaryItemResponse,
    EnrollmentBalanceResponse,
    EnrollmentCreatedResponse,
    PaymentDistributionResponse,
    PaymentResultResponse,
    StudentInfoResponse,
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
    )


@router.post(
    "/register",
    response_model=EnrollmentCreatedResponse,
    status_code=201,
    summary="Registrar matrícula para un estudiante",
    description=(
        "Genera automáticamente la matrícula para un estudiante. "
        "Calcula el costo base según su grado, asigna los complementarios "
        "activos con uso_matricula=True, y suma el primer mes de pensión."
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
            f"Matrícula registrada exitosamente. "
            f"Total a pagar: ${result.valor_total:,}"
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
        (a.concepto, a.complementario_id, a.monto)
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
    "/register/massive/csv",
    status_code=201,
    summary="Registrar matrículas masivamente vía CSV",
)
async def register_massive_csv(
    session: SessionDep,
    periodo_id: int,
    anio: int,
    file: UploadFile = File(...),
):
    use_case = MassEnrollment(session=session)

    content = await file.read()
    return use_case.execute(content, periodo_id, anio)


@router.post(
    "/register/massive/txt",
    status_code=201,
    summary="Registrar matrículas masivamente vía TXT",
)
async def register_massive_txt(
    session: SessionDep,
    periodo_id: int,
    anio: int,
    file: UploadFile = File(...),
):
    use_case = MassEnrollment(session=session)

    content = await file.read()
    return use_case.execute(content, periodo_id, anio)


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
        tipo_complementario=request.tipo_complementario,
        anio=request.anio,
        valor=request.valor,
        estado=request.estado_complemento,
        uso_matricula=request.uso_matricula,
    )
    return {"mensaje": "Complementario creado exitosamente", "complementario_id": comp_id}


@router.post(
    "/{matricula_id}/complementary/assign",
    status_code=201,
    summary="Asignar un complementario a una matrícula existente",
)
async def assign_complementary(
    session: SessionDep,
    matricula_id: int,
    request: AssignComplementaryRequest,
):
    use_case = AssignComplementary(session=session)

    try:
        detalle_id = use_case.execute(
            matricula_id=matricula_id,
            complementary_id=request.complementario_id,
            descuento=request.descuento,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {"mensaje": "Complementario asignado exitosamente a la matrícula", "detalle_id": detalle_id}
