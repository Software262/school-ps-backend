from fastapi import APIRouter, HTTPException
from sqlmodel import select, col
from app.core.db import SessionDep
from app.modules.tuition.schemas.request import PaymentCreateRequest
from app.modules.tuition.schemas.response import (
    TuitionAccountResponse,
    TuitionInstallmentResponse,
    TuitionStudentSearchListResponse,
    TuitionStudentSearchItem,
)
from app.modules.tuition.application.register_tuition_payment import (
    RegisterTuitionPaymentUseCase,
)
from app.modules.tuition.application.get_student_tuition import GetStudentTuitionUseCase
from app.modules.enrollment.infrastructure.models import Estudiante, Grado

from datetime import datetime
from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.core.db import SessionDep
from app.modules.enrollment.infrastructure.models import Estudiante
from app.modules.tuition.infrastructure.enrollment_adapter import TuitionEnrollmentAdapter
# Asegúrate de tener importado tu GetStudentTuitionUseCase

router = APIRouter()


@router.get("/search", response_model=TuitionStudentSearchListResponse)
def search_tuition_students(session: SessionDep, q: str):
    query = (
        select(Estudiante, Grado)
        .join(Grado, col(Estudiante.grado_id) == col(Grado.id))
        .where(
            (col(Estudiante.nombre).ilike(f"%{q}%")) | (col(Estudiante.documento).ilike(f"%{q}%"))
        )
    )
    
    results = session.exec(query).all()
    
    estudiantes_list = []
    for estudiante, grado in results:
        estudiantes_list.append(
            TuitionStudentSearchItem(
                estudiante_id=estudiante.id or 0,
                documento=estudiante.documento,
                nombre=estudiante.nombre,
                grado_nombre=grado.nombre,
                estado_matricula="activo" if estudiante.activo else "inactivo",
            )
        )
        
    return TuitionStudentSearchListResponse(estudiantes=estudiantes_list)


@router.get("/student/documento/{documento}", response_model=TuitionAccountResponse)
def get_tuition_by_documento(session: SessionDep, documento: str):
    estudiante = session.exec(
        select(Estudiante).where(Estudiante.documento == documento)
    ).first()
    if not estudiante:
        raise HTTPException(
            status_code=404, detail="No se encontró ningún estudiante con esa cédula."
        )

    if not estudiante.id or not estudiante.grado_id:
        raise HTTPException(
            status_code=500, detail="Error: El estudiante no tiene ID o grado válido."
        )

    use_case = GetStudentTuitionUseCase(session)
    account_response = use_case.execute(estudiante.id)
    
    # Si no tiene cuenta de pensión registrada, la creamos automáticamente al vuelo
    if not account_response:
        try:
            adapter = TuitionEnrollmentAdapter(session)
            adapter.create_pension_account(
                student_id=estudiante.id,
                grade_id=estudiante.grado_id,
                year=datetime.now().year
            )
            session.commit()
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Error al crear automáticamente la cuenta de pensión: {str(e)}"
            )
        
        # Volvemos a ejecutar el use case para obtener la información recién creada
        account_response = use_case.execute(estudiante.id)
        if not account_response:
            raise HTTPException(
                status_code=404,
                detail="No se pudo registrar ni recuperar la cuenta de pensión del estudiante.",
            )

    return account_response


@router.get("/student/{student_id}", response_model=TuitionAccountResponse)
def get_tuition_account(session: SessionDep, student_id: int):
    use_case = GetStudentTuitionUseCase(session)
    account_response = use_case.execute(student_id)
    if not account_response:
        raise HTTPException(
            status_code=404,
            detail="No se encontró cuenta de pensión para el estudiante",
        )
    return account_response


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
