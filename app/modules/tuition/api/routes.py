from fastapi import APIRouter, HTTPException
from sqlmodel import select
from app.core.db import SessionDep
from app.modules.tuition.schemas.request import PaymentCreateRequest
from app.modules.tuition.schemas.response import (
    TuitionAccountResponse,
    TuitionInstallmentResponse,
)
from app.modules.tuition.application.register_tuition_payment import (
    RegisterTuitionPaymentUseCase,
)
from app.modules.tuition.application.get_student_tuition import GetStudentTuitionUseCase
from app.modules.enrollment.infrastructure.models import Estudiante

router = APIRouter()


def _build_account_response(account) -> TuitionAccountResponse:
    """Helper: construye TuitionAccountResponse con las 12 cuotas mensuales."""
    TOTAL_MONTHS = 12  # TODO: leer desde ParametrizarPension.num_meses cuando el Tech Lead agregue la columna
    monthly_value = account.valor_total  # El valor guardado es el costo mensual

    totals_by_month: dict[int, int] = {}
    for inst in account.installments:
        totals_by_month[inst.mes] = totals_by_month.get(inst.mes, 0) + inst.valor_pagado

    installments_response = []
    for mes in range(1, TOTAL_MONTHS + 1):
        mes_trans = [i for i in account.installments if i.mes == mes]
        total_pagado = totals_by_month.get(mes, 0)
        saldo_pendiente = max(monthly_value - total_pagado, 0)

        if mes_trans:
            last_inst = mes_trans[-1]
            installments_response.append(
                TuitionInstallmentResponse(
                    id=last_inst.id or 0,
                    mes=mes,
                    cuota=last_inst.cuota,
                    valor_total=monthly_value,
                    valor_pagado=last_inst.valor_pagado,
                    total_pagado_mes=total_pagado,
                    saldo_pendiente=saldo_pendiente,
                    fecha_pago=last_inst.fecha_pago,
                    faltante=saldo_pendiente > 0,
                )
            )
        else:
            installments_response.append(
                TuitionInstallmentResponse(
                    id=-mes,
                    mes=mes,
                    cuota=mes,
                    valor_total=monthly_value,
                    valor_pagado=0,
                    total_pagado_mes=0,
                    saldo_pendiente=monthly_value,
                    fecha_pago=None,
                    faltante=True,
                )
            )

    return TuitionAccountResponse(
        estudiante_id=account.estudiante_id,
        valor_total_anual=account.valor_total,
        estado_pension_general=account.estado_pension,
        installments=installments_response,
    )


@router.get("/student/documento/{documento}", response_model=TuitionAccountResponse)
def get_tuition_by_documento(session: SessionDep, documento: str):
    estudiante = session.exec(
        select(Estudiante).where(Estudiante.documento == documento)
    ).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="No se encontró ningún estudiante con esa cédula.")

    if not estudiante.id:
        raise HTTPException(status_code=500, detail="Error: El estudiante no tiene ID válido.")

    use_case = GetStudentTuitionUseCase(session)
    account = use_case.execute(estudiante.id)
    if not account:
        raise HTTPException(status_code=404, detail="El estudiante no tiene cuenta de pensión registrada.")
    return _build_account_response(account)


@router.get("/student/{student_id}", response_model=TuitionAccountResponse)
def get_tuition_account(session: SessionDep, student_id: int):
    use_case = GetStudentTuitionUseCase(session)
    account = use_case.execute(student_id)
    if not account:
        raise HTTPException(status_code=404, detail="No se encontró cuenta de pensión para el estudiante")
    return _build_account_response(account)


@router.post("/payment", response_model=TuitionInstallmentResponse)
def register_payment(session: SessionDep, request: PaymentCreateRequest):
    use_case = RegisterTuitionPaymentUseCase(session)
    try:
        installment = use_case.execute(request)
        return TuitionInstallmentResponse(
            id=installment.id or 0,
            mes=installment.mes,
            cuota=installment.cuota,
            valor_total=installment.valor_total,
            valor_pagado=installment.valor_pagado,
            total_pagado_mes=installment.total_pagado_mes,
            saldo_pendiente=installment.saldo_pendiente,
            fecha_pago=installment.fecha_pago,
            faltante=installment.faltante,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
