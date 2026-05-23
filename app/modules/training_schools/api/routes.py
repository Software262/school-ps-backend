from typing import List
from fastapi import APIRouter, status

from app.core.db import SessionDep
from app.shared.utils.response import Response
from app.modules.training_schools.application.create_enrollment import CreateEnrollment
from app.modules.training_schools.application.register_payment import RegisterPayment
from app.modules.training_schools.application.unsubscribe_student import UnsubscribeStudent
from app.modules.training_schools.application.get_student_status import GetStudentStatus
from app.modules.training_schools.application.list_enrollments import ListEnrollments
from app.modules.training_schools.schemas.request import (
    CreateEnrollmentRequest,
    RegisterPaymentRequest,
    UnsubscribeRequest,
)
from app.modules.training_schools.schemas.response import (
    EnrollmentResponse,
    PaymentResponse,
    GeneralStatusResponse,
)

router = APIRouter()


@router.post("/enroll", status_code=status.HTTP_201_CREATED)
async def enroll_student(session: SessionDep, request: CreateEnrollmentRequest):
    use_case = CreateEnrollment(session=session)
    enrollment = await use_case.execute(request)

    if not enrollment:
        return Response(
            data=None,
            message="No se pudo inscribir al estudiante. Verifique que no esté previamente inscrito en este mes y que el programa esté activo.",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"message": "Inscripción fallida o duplicada"}
        ).to_dict()

    return Response(
        data=EnrollmentResponse(
            id=enrollment.id,
            complementario_id=enrollment.complementario_id,
            estudiante_id=enrollment.estudiante_id,
            fecha_registro=enrollment.fecha_registro,
            mes=enrollment.mes,
            activo=enrollment.activo,
            estado_escuela=enrollment.estado_escuela,
            motivo_baja=getattr(enrollment, "motivo_baja", None),
        ),
        message="Estudiante inscrito exitosamente en la escuela de formación.",
        status_code=status.HTTP_201_CREATED,
        details={"message": "Inscripción exitosa"}
    ).to_dict()


@router.post("/payments", status_code=status.HTTP_200_OK)
async def register_payment(session: SessionDep, request: RegisterPaymentRequest):
    use_case = RegisterPayment(session=session)
    payment = await use_case.execute(request)

    if not payment:
        return Response(
            data=None,
            message="No se pudo registrar el pago. Verifique que exista una inscripción activa para el estudiante en el mes seleccionado.",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"message": "Pago fallido"}
        ).to_dict()

    return Response(
        data=PaymentResponse(
            id=payment.id,
            complementario_id=payment.complementario_id,
            estudiante_id=payment.estudiante_id,
            mes=payment.mes,
            estado_escuela=payment.estado_escuela,
            activo=payment.activo,
            updated_at=payment.updated_at,
        ),
        message="Pago registrado exitosamente para la mensualidad correspondiente.",
        status_code=status.HTTP_200_OK,
        details={"message": "Pago exitoso"}
    ).to_dict()


@router.patch("/enrollments/{student_id}/{complementario_id}/{mes}/unsubscribe", status_code=status.HTTP_200_OK)
async def unsubscribe_student(
    session: SessionDep, student_id: int, complementario_id: int, mes: str, request: UnsubscribeRequest
):
    use_case = UnsubscribeStudent(session=session)
    enrollment = await use_case.execute(student_id, complementario_id, mes, request)

    if not enrollment:
        return Response(
            data=None,
            message="No se pudo procesar la baja del estudiante. Verifique los datos de inscripción.",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"message": "Baja fallida"}
        ).to_dict()

    return Response(
        data=EnrollmentResponse(
            id=enrollment.id,
            complementario_id=enrollment.complementario_id,
            estudiante_id=enrollment.estudiante_id,
            fecha_registro=enrollment.fecha_registro,
            mes=enrollment.mes,
            activo=enrollment.activo,
            estado_escuela=enrollment.estado_escuela,
            motivo_baja=getattr(enrollment, "motivo_baja", None),
        ),
        message="Estudiante dado de baja exitosamente de la escuela de formación.",
        status_code=status.HTTP_200_OK,
        details={"message": "Baja exitosa"}
    ).to_dict()


@router.get("/students/{student_id}/status", response_model=dict)
async def get_student_status(session: SessionDep, student_id: int):
    use_case = GetStudentStatus(session=session)
    status_data = await use_case.execute(student_id)

    return Response(
        data=GeneralStatusResponse(
            estudiante_id=status_data["estudiante_id"],
            paz_y_salvo=status_data["paz_y_salvo"],
            detalle=status_data["detalle"],
        ),
        message="Estado de paz y salvo consolidado de las escuelas de formación.",
        status_code=status.HTTP_200_OK,
        details={"message": "Consulta de estado exitosa"}
    ).to_dict()


@router.get("/students/{student_id}/enrollments")
async def list_student_enrollments(session: SessionDep, student_id: int):
    use_case = ListEnrollments(session=session)
    enrollments = await use_case.execute_for_student(student_id)

    enrollment_responses = [
        EnrollmentResponse(
            id=e.id,
            complementario_id=e.complementario_id,
            estudiante_id=e.estudiante_id,
            fecha_registro=e.fecha_registro,
            mes=e.mes,
            activo=e.activo,
            estado_escuela=e.estado_escuela,
            motivo_baja=getattr(e, "motivo_baja", None),
        )
        for e in enrollments
    ]

    return Response(
        data=enrollment_responses,
        message="Inscripciones del estudiante obtenidas con éxito.",
        status_code=status.HTTP_200_OK,
        details={"message": "Listado de inscripciones exitoso"}
    ).to_dict()


@router.get("/programs/{complementario_id}/enrollments")
async def list_program_enrollments(session: SessionDep, complementario_id: int):
    use_case = ListEnrollments(session=session)
    enrollments = await use_case.execute_for_program(complementario_id)

    enrollment_responses = [
        EnrollmentResponse(
            id=e.id,
            complementario_id=e.complementario_id,
            estudiante_id=e.estudiante_id,
            fecha_registro=e.fecha_registro,
            mes=e.mes,
            activo=e.activo,
            estado_escuela=e.estado_escuela,
            motivo_baja=getattr(e, "motivo_baja", None),
        )
        for e in enrollments
    ]

    return Response(
        data=enrollment_responses,
        message="Estudiantes inscritos en el programa obtenidos con éxito.",
        status_code=status.HTTP_200_OK,
        details={"message": "Listado de inscritos exitoso"}
    ).to_dict()
