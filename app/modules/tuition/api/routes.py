from fastapi import APIRouter, HTTPException
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

router = APIRouter()


@router.get("/student/{student_id}", response_model=TuitionAccountResponse)
def get_tuition_account(session: SessionDep, student_id: int):
    use_case = GetStudentTuitionUseCase(session)
    account = use_case.execute(student_id)
    if not account:
        raise HTTPException(status_code=404, detail="No se encontró cuenta de pensión para el estudiante")

    # Agrupar cuotas por mes para calcular acumulados
    installments_by_month: dict[int, int] = {}
    for inst in account.installments:
        installments_by_month[inst.mes] = installments_by_month.get(inst.mes, 0) + inst.valor_pagado

    monthly_value = account.valor_total // 10

    return TuitionAccountResponse(
        estudiante_id=account.estudiante_id,
        valor_total_anual=account.valor_total,
        estado_pension_general=account.estado_pension,
        installments=[
            TuitionInstallmentResponse(
                id=inst.id or 0,
                mes=inst.mes,
                cuota=inst.cuota,
                valor_total=inst.valor_total,
                valor_pagado=inst.valor_pagado,
                total_pagado_mes=installments_by_month.get(inst.mes, 0),
                saldo_pendiente=max(monthly_value - installments_by_month.get(inst.mes, 0), 0),
                fecha_pago=inst.fecha_pago,
                faltante=inst.faltante,
            )
            for inst in account.installments
        ],
    )


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
