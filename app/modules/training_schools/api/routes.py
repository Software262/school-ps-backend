from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status

from app.core.db import SessionDep
from app.modules.training_schools.application.create_enrollment import CreateEnrollment
from app.modules.training_schools.application.get_student_status import GetStudentStatus
from app.modules.training_schools.application.list_enrollments import ListEnrollments
from app.modules.training_schools.application.register_payment import RegisterPayment
from app.modules.training_schools.application.unsubscribe_student import (
    UnsubscribeStudent,
)
from app.modules.training_schools.infrastructure.models import DetalleEscuelaFormacion
from app.modules.enrollment.infrastructure.models import Complementario, Estudiante
from app.modules.training_schools.schemas.request import (
    CreateEnrollmentRequest,
    CreateProgramRequest,
    RegisterPaymentRequest,
    UnsubscribeRequest,
)
from app.modules.training_schools.schemas.response import (
    EnrollmentResponse,
    GeneralStatusResponse,
    MonthlyStatusResponse,
    PaymentResponse,
    ProgramResponse,
    StudentResponse,
)
from app.shared.utils.response import Response

router = APIRouter()


def to_enrollment_response(
    session: SessionDep, enrollment: DetalleEscuelaFormacion
) -> EnrollmentResponse:
    if enrollment.id is None:
        raise ValueError("Enrollment must be persisted before building a response.")

    student = session.get(Estudiante, enrollment.estudiante_id)
    program = session.get(Complementario, enrollment.complementario_id)

    return EnrollmentResponse(
        id=enrollment.id,
        complementario_id=enrollment.complementario_id,
        estudiante_id=enrollment.estudiante_id,
        estudiante_nombre=student.nombre if student else None,
        estudiante_documento=student.documento if student else None,
        disciplina_nombre=program.tipo_complementario if program else None,
        fecha_registro=enrollment.fecha_registro,
        mes=enrollment.mes,
        activo=enrollment.activo,
        estado_escuela=enrollment.estado_escuela,
        motivo_baja=getattr(enrollment, "motivo_baja", None),
    )


def to_program_response(program) -> ProgramResponse:
    if program.id is None:
        raise ValueError("Program must be persisted before building a response.")

    return ProgramResponse(
        id=program.id,
        nombre=program.tipo_complementario,
        valor=program.valor,
        estado=program.estado_complemento,
    )


def to_student_response(student) -> StudentResponse:
    if student.id is None:
        raise ValueError("Student must be persisted before building a response.")

    return StudentResponse(
        id=student.id,
        nombre=student.nombre,
        documento=student.documento,
        activo=student.activo,
    )


def to_payment_response(
    session: SessionDep, payment: DetalleEscuelaFormacion
) -> PaymentResponse:
    if payment.id is None:
        raise ValueError("Payment record must be persisted before building a response.")

    student = session.get(Estudiante, payment.estudiante_id)
    program = session.get(Complementario, payment.complementario_id)

    return PaymentResponse(
        id=payment.id,
        complementario_id=payment.complementario_id,
        estudiante_id=payment.estudiante_id,
        estudiante_nombre=student.nombre if student else None,
        estudiante_documento=student.documento if student else None,
        disciplina_nombre=program.tipo_complementario if program else None,
        mes=payment.mes,
        estado_escuela=payment.estado_escuela,
        activo=payment.activo,
        updated_at=payment.updated_at or datetime.now(),
    )


@router.post("/enroll", status_code=status.HTTP_201_CREATED)
async def enroll_student(session: SessionDep, request: CreateEnrollmentRequest):
    use_case = CreateEnrollment(session=session)
    enrollment = await use_case.execute(request)

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No se pudo registrar el mes. Verifique que el estudiante exista, "
                "que este activo, que el programa este activo y que no exista ya "
                "un registro para ese estudiante, disciplina y mes."
            ),
        )

    return Response(
        data=to_enrollment_response(session, enrollment),
        message="Registro mensual creado correctamente.",
        status_code=status.HTTP_201_CREATED,
        details={"message": "Registro mensual exitoso"},
    ).to_dict()


@router.post("/payments", status_code=status.HTTP_200_OK)
async def register_payment(session: SessionDep, request: RegisterPaymentRequest):
    use_case = RegisterPayment(session=session)
    payment = await use_case.execute(request)

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No se pudo marcar el mes como pagado. Verifique que exista un "
                "registro activo para el estudiante, disciplina y mes seleccionados."
            ),
        )

    return Response(
        data=to_payment_response(session, payment),
        message="Mes marcado como pagado correctamente.",
        status_code=status.HTTP_200_OK,
        details={"message": "Actualizacion de pago exitosa"},
    ).to_dict()


@router.patch("/payments/unmark", status_code=status.HTTP_200_OK)
async def unmark_payment(session: SessionDep, request: RegisterPaymentRequest):
    use_case = RegisterPayment(session=session)
    payment = await use_case.execute_unmark(request)

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "No se pudo desmarcar el pago. Verifique que exista un registro "
                "activo para el estudiante, disciplina y mes seleccionados."
            ),
        )

    return Response(
        data=to_payment_response(session, payment),
        message="Mes desmarcado como pagado correctamente.",
        status_code=status.HTTP_200_OK,
        details={"message": "Pago desmarcado exitosamente"},
    ).to_dict()


@router.patch(
    "/enrollments/{student_id}/{complementario_id}/{mes}/unsubscribe",
    status_code=status.HTTP_200_OK,
)
async def unsubscribe_monthly_record(
    session: SessionDep,
    student_id: int,
    complementario_id: int,
    mes: str,
    request: UnsubscribeRequest,
):
    use_case = UnsubscribeStudent(session=session)
    enrollment = await use_case.execute(student_id, complementario_id, mes, request)

    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo procesar la baja del registro mensual.",
        )

    return Response(
        data=to_enrollment_response(session, enrollment),
        message="Registro mensual dado de baja correctamente.",
        status_code=status.HTTP_200_OK,
        details={"message": "Baja mensual exitosa"},
    ).to_dict()


@router.patch(
    "/students/{student_id}/programs/{complementario_id}/unsubscribe",
    status_code=status.HTTP_200_OK,
)
async def unsubscribe_student_from_program(
    session: SessionDep,
    student_id: int,
    complementario_id: int,
    request: UnsubscribeRequest,
):
    use_case = UnsubscribeStudent(session=session)
    enrollments = await use_case.execute_for_program(
        student_id, complementario_id, request
    )

    if not enrollments:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se encontraron registros activos para dar de baja.",
        )

    return Response(
        data=[
            to_enrollment_response(session, enrollment) for enrollment in enrollments
        ],
        message="Estudiante dado de baja de la disciplina correctamente.",
        status_code=status.HTTP_200_OK,
        details={"message": "Baja de disciplina exitosa"},
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
        message="Estado consolidado de escuelas de formacion.",
        status_code=status.HTTP_200_OK,
        details={"message": "Consulta de estado exitosa"},
    ).to_dict()


@router.get("/students/{student_id}/programs/{complementario_id}/monthly-status")
async def get_monthly_status(
    session: SessionDep, student_id: int, complementario_id: int
):
    use_case = GetStudentStatus(session=session)
    status_data = await use_case.execute_monthly(student_id, complementario_id)

    return Response(
        data=MonthlyStatusResponse(
            estudiante_id=status_data["estudiante_id"],
            complementario_id=status_data["complementario_id"],
            paz_y_salvo=status_data["paz_y_salvo"],
            detalle=status_data["detalle"],
            meses=[
                to_enrollment_response(session, enrollment)
                for enrollment in status_data["meses"]
            ],
        ),
        message="Estado mensual de la disciplina obtenido correctamente.",
        status_code=status.HTTP_200_OK,
        details={"message": "Consulta mensual exitosa"},
    ).to_dict()


@router.get("/enrollments")
async def list_enrollments(
    session: SessionDep,
    student_id: int | None = Query(default=None, ge=1),
    complementario_id: int | None = Query(default=None, ge=1),
    mes: str | None = Query(default=None, min_length=3, max_length=20),
    activo: bool | None = Query(default=None),
    estado_escuela: bool | None = Query(default=None),
):
    use_case = ListEnrollments(session=session)
    enrollments = await use_case.execute(
        student_id=student_id,
        complementario_id=complementario_id,
        mes=mes,
        activo=activo,
        estado_escuela=estado_escuela,
    )

    return Response(
        data=[
            to_enrollment_response(session, enrollment) for enrollment in enrollments
        ],
        message="Registros mensuales obtenidos correctamente.",
        status_code=status.HTTP_200_OK,
        details={"message": "Listado filtrado exitoso"},
    ).to_dict()


@router.get("/students")
async def search_students(
    session: SessionDep,
    query: str = Query(min_length=1, max_length=100),
):
    use_case = ListEnrollments(session=session)
    students = await use_case.execute_students(query)

    return Response(
        data=[to_student_response(student) for student in students],
        message="Estudiantes encontrados correctamente.",
        status_code=status.HTTP_200_OK,
        details={"message": "Busqueda de estudiantes exitosa"},
    ).to_dict()


@router.get("/programs")
async def list_available_programs(session: SessionDep):
    use_case = ListEnrollments(session=session)
    programs = await use_case.execute_programs()

    return Response(
        data=[to_program_response(program) for program in programs],
        message="Disciplinas disponibles obtenidas correctamente.",
        status_code=status.HTTP_200_OK,
        details={"message": "Listado de disciplinas exitoso"},
    ).to_dict()


@router.post("/programs", status_code=status.HTTP_201_CREATED)
async def create_program(session: SessionDep, request: CreateProgramRequest):
    use_case = ListEnrollments(session=session)
    program = await use_case.execute_create_program(request)

    if not program:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo crear la disciplina. Verifique que no exista previamente.",
        )

    return Response(
        data=to_program_response(program),
        message="Disciplina creada correctamente.",
        status_code=status.HTTP_201_CREATED,
        details={"message": "Creacion de disciplina exitosa"},
    ).to_dict()


@router.get("/students/{student_id}/enrollments")
async def list_student_enrollments(session: SessionDep, student_id: int):
    use_case = ListEnrollments(session=session)
    enrollments = await use_case.execute_for_student(student_id)

    return Response(
        data=[
            to_enrollment_response(session, enrollment) for enrollment in enrollments
        ],
        message="Registros mensuales del estudiante obtenidos correctamente.",
        status_code=status.HTTP_200_OK,
        details={"message": "Listado de estudiante exitoso"},
    ).to_dict()


@router.get("/programs/{complementario_id}/enrollments")
async def list_program_enrollments(session: SessionDep, complementario_id: int):
    use_case = ListEnrollments(session=session)
    enrollments = await use_case.execute_for_program(complementario_id)

    return Response(
        data=[
            to_enrollment_response(session, enrollment) for enrollment in enrollments
        ],
        message="Registros mensuales de la disciplina obtenidos correctamente.",
        status_code=status.HTTP_200_OK,
        details={"message": "Listado de disciplina exitoso"},
    ).to_dict()
