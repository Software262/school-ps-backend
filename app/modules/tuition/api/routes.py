from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.modules.tuition.schemas.request import PaymentCreateRequest
from app.modules.tuition.schemas.response import TuitionAccountResponse, TuitionInstallmentResponse
from app.modules.tuition.infrastructure.repositories import SQLModelTuitionRepository
from app.modules.tuition.application.register_tuition_payment import RegisterTuitionPaymentUseCase
from app.modules.tuition.application.get_student_tuition import GetStudentTuitionUseCase

# Assuming a dependency for session exists globally, otherwise you can define one here
def get_session():
    pass

router = APIRouter(prefix="/tuition", tags=["tuition"])

@router.get("/student/{student_id}", response_model=TuitionAccountResponse)
def get_tuition_account(student_id: int, session: Session = Depends(get_session)):
    repo = SQLModelTuitionRepository(session)
    use_case = GetStudentTuitionUseCase(repo)
    account = use_case.execute(student_id)
    if not account:
        raise HTTPException(status_code=404, detail="Tuition account not found")
        
    return TuitionAccountResponse(
        estudiante_id=account.estudiante_id,
        valor_total_anual=account.valor_total,
        estado_pension_general=account.estado_pension,
        installments=[
            TuitionInstallmentResponse(
                id=inst.id,
                mes=inst.mes,
                cuota=inst.cuota,
                valor_total=inst.valor_total,
                valor_pagado=inst.valor_pagado,
                fecha_pago=inst.fecha_pago,
                faltante=inst.faltante
            ) for inst in account.installments
        ]
    )

@router.post("/payment", response_model=TuitionInstallmentResponse)
def register_payment(request: PaymentCreateRequest, session: Session = Depends(get_session)):
    repo = SQLModelTuitionRepository(session)
    use_case = RegisterTuitionPaymentUseCase(repo)
    try:
        installment = use_case.execute(request)
        return TuitionInstallmentResponse(
            id=installment.id,
            mes=installment.mes,
            cuota=installment.cuota,
            valor_total=installment.valor_total,
            valor_pagado=installment.valor_pagado,
            fecha_pago=installment.fecha_pago,
            faltante=installment.faltante
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
