from fastapi import APIRouter, HTTPException, Query, status

from app.core.db import SessionDep
from app.modules.training_schools.application.enroll_student import EnrollStudent
from app.modules.training_schools.application.get_enrollments_detail import (
    GetEnrollmentsDetail,
)
from app.modules.training_schools.application.get_paz_y_salvo import GetPazYSalvo
from app.modules.training_schools.application.get_periods import GetPeriods
from app.modules.training_schools.application.get_programs import GetPrograms
from app.modules.training_schools.application.register_payment import RegisterPayment
from app.modules.training_schools.application.search_students import SearchStudents
from app.modules.training_schools.application.withdraw_student import WithdrawStudent
from app.modules.training_schools.schemas.request import (
    EnrollStudentRequest,
    RegisterPaymentRequest,
    WithdrawStudentRequest,
)
from app.shared.utils.response import Response

router = APIRouter()


@router.get("/programs", summary="Listar programas de escuelas de formación")
async def get_programs(session: SessionDep):
    use_case = GetPrograms(session)
    data = await use_case.execute()
    return Response(
        data=data,
        message="Programas obtenidos exitosamente",
        status_code=status.HTTP_200_OK,
    ).to_dict()


@router.get("/periods", summary="Listar períodos académicos activos")
async def get_periods(session: SessionDep):
    use_case = GetPeriods(session)
    data = await use_case.execute()
    return Response(
        data=data,
        message="Períodos obtenidos exitosamente",
        status_code=status.HTTP_200_OK,
    ).to_dict()


@router.get("/students/search", summary="Buscar estudiantes por código o nombre")
async def search_students(
    session: SessionDep,
    q: str = Query(..., min_length=2, description="Código o nombre del estudiante"),
):
    use_case = SearchStudents(session)
    try:
        data = await use_case.execute(q)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return Response(
        data=data,
        message="Estudiantes encontrados",
        status_code=status.HTTP_200_OK,
    ).to_dict()


@router.get(
    "/enrollments/{periodo_id}",
    summary="Listar inscripciones por período con información del estudiante",
)
async def get_enrollments(periodo_id: int, session: SessionDep):
    use_case = GetEnrollmentsDetail(session)
    data = await use_case.execute(periodo_id)
    return Response(
        data=data,
        message="Inscripciones obtenidas exitosamente",
        status_code=status.HTTP_200_OK,
    ).to_dict()


@router.post("/enroll", summary="Inscribir estudiante en escuela de formación")
async def enroll_student(session: SessionDep, request: EnrollStudentRequest):
    use_case = EnrollStudent(session)
    try:
        data = await use_case.execute(
            request.estudiante_id,
            request.complementario_id,
            request.periodo_id,
            request.mes,
            request.usuario_id,
            observaciones=request.observaciones,
            valor_acordado=request.valor_acordado,
            numero_comprobante=request.numero_comprobante,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return Response(
        data=data,
        message="Estudiante inscrito exitosamente",
        status_code=status.HTTP_201_CREATED,
    ).to_dict()


@router.post("/payment", summary="Registrar pago parcial o total")
async def register_payment(session: SessionDep, request: RegisterPaymentRequest):
    use_case = RegisterPayment(session)
    try:
        data = await use_case.execute(
            request.enrollment_id, request.monto, request.usuario_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return Response(
        data=data,
        message="Pago registrado exitosamente",
        status_code=status.HTTP_200_OK,
    ).to_dict()


@router.post("/withdraw", summary="Retirar estudiante de escuela de formación")
async def withdraw_student(session: SessionDep, request: WithdrawStudentRequest):
    use_case = WithdrawStudent(session)
    try:
        data = await use_case.execute(
            request.enrollment_id, request.motivo, request.usuario_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return Response(
        data=data,
        message="Retiro registrado exitosamente",
        status_code=status.HTTP_200_OK,
    ).to_dict()


@router.get(
    "/paz-y-salvo/{estudiante_id}",
    summary="Consultar paz y salvo del módulo para un estudiante",
)
async def get_paz_y_salvo(estudiante_id: int, session: SessionDep):
    use_case = GetPazYSalvo(session)
    paz_y_salvo = await use_case.execute(estudiante_id)
    return Response(
        data={"estudiante_id": estudiante_id, "paz_y_salvo": paz_y_salvo},
        message="Estado de paz y salvo obtenido",
        status_code=status.HTTP_200_OK,
    ).to_dict()
