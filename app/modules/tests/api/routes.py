from typing import Annotated

from fastapi import APIRouter, Query, status
from sqlalchemy.exc import IntegrityError

from app.core.db import SessionDep
from app.modules.tests.application.assign_massive import AssignMassiveTests
from app.modules.tests.application.create_internal import CreateInternalTest
from app.modules.tests.application.delete_complementary import (
    DeleteTestComplementary,
)
from app.modules.tests.application.delete_internal import DeleteInternalTest
from app.modules.tests.application.get_available import GetAvailableTests
from app.modules.tests.application.get_estudiantes import GetEstudiantes
from app.modules.tests.application.get_grados import GetGrados
from app.modules.tests.application.get_internal import GetInternalTests
from app.modules.tests.application.get_internal_by_id import GetInternalTestById
from app.modules.tests.application.get_internal_by_student import (
    GetInternalTestsByStudent,
)
from app.modules.tests.application.get_periodos import GetPeriodos
from app.modules.tests.application.get_student_status import GetStudentTestStatus
from app.modules.tests.application.register_payment import RegisterTestPayment
from app.modules.tests.application.update_complementary import (
    UpdateTestComplementary,
)
from app.modules.tests.application.update_internal import UpdateInternalTest
from app.modules.tests.schemas.request import (
    ComplementaryUpdateBody,
    CreateTestDetailRequest,
    MassiveAssignmentRequest,
    PaymentRequest,
    UpdateTestDetailRequest,
)
from app.modules.tests.schemas.response import (
    CreateTestDetailResponse,
    UpdateTestDetailResponse,
)
from app.shared.schemas.filter_pagination_request import FilterPagination
from app.shared.utils.response import Response

router = APIRouter()


@router.get("/available-tests")
async def get_available_tests(session: SessionDep):
    try:
        app_service = GetAvailableTests(session=session)
        data = await app_service.execute()
        return Response(
            data=[
                {
                    "id": d.id,
                    "nombre": d.tipo_complementario,
                    "valor": d.valor,
                    "anio": d.anio,
                }
                for d in data
            ],
            message="Pruebas disponibles obtenidas",
            status_code=status.HTTP_200_OK,
            details={"count": len(data)},
        ).to_dict()
    except Exception as e:
        return Response(
            data=None,
            message="Error al obtener pruebas disponibles",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)},
        ).to_dict()


@router.get("/grados")
async def get_grados(session: SessionDep):
    try:
        app_service = GetGrados(session=session)
        grados = await app_service.execute()
        return Response(
            data=[{"id": g.id, "nombre": g.nombre} for g in grados],
            message="Grados obtenidos",
            status_code=200,
            details={"count": len(grados)},
        ).to_dict()
    except Exception as e:
        return Response(
            data=None,
            message="Error al obtener grados",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)},
        ).to_dict()


@router.get("/periodos")
async def get_periodos(session: SessionDep):
    try:
        app_service = GetPeriodos(session=session)
        periodos = await app_service.execute()
        return Response(
            data=[
                {
                    "id": p.id,
                    "nombre": p.nombre,
                    "fecha": p.fecha,
                }
                for p in periodos
            ],
            message="Periodos obtenidos",
            status_code=200,
            details={"count": len(periodos)},
        ).to_dict()
    except Exception as e:
        return Response(
            data=None,
            message="Error al obtener periodos",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)},
        ).to_dict()


@router.get("/estudiantes")
async def get_estudiantes(session: SessionDep):
    try:
        app_service = GetEstudiantes(session=session)
        students = await app_service.execute()
        return Response(
            data=[
                {
                    "id": s.id,
                    "nombre": s.nombre,
                    "documento": s.documento,
                    "grado_id": s.grado_id,
                }
                for s in students
            ],
            message="Estudiantes obtenidos",
            status_code=200,
            details={"count": len(students)},
        ).to_dict()
    except Exception as e:
        return Response(
            data=None,
            message="Error al obtener estudiantes",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)},
        ).to_dict()


@router.post("/assign-massive")
async def assign_massive_tests(session: SessionDep, request: MassiveAssignmentRequest):
    try:
        app_service = AssignMassiveTests(session=session)
        result = await app_service.execute(request)
        assigned = result.get("assigned", [])
        skipped = result.get("skipped", 0)
        message = result.get("message", "")
        return Response(
            data=assigned,
            message=str(message),
            status_code=status.HTTP_201_CREATED if assigned else status.HTTP_200_OK,
            details={
                "count": len(assigned) if isinstance(assigned, list) else 0,
                "skipped": int(skipped) if isinstance(skipped, (int, str)) else 0,
            },
        ).to_dict()
    except Exception as e:
        return Response(
            data=None,
            message="Error al asignar masivamente",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)},
        ).to_dict()


@router.post("/assign-individual")
async def assign_individual_test(session: SessionDep, request: CreateTestDetailRequest):
    try:
        app_service = CreateInternalTest(session=session)
        data = await app_service.execute(request)
        return Response(
            data={"id": data.id},
            message="Prueba asignada exitosamente al estudiante",
            status_code=status.HTTP_201_CREATED,
            details={"id": data.id},
        ).to_dict()
    except ValueError as e:
        if str(e) == "duplicate_assignment":
            return Response(
                data=None,
                message="Este estudiante ya tiene esta prueba asignada",
                status_code=status.HTTP_200_OK,
                details={"duplicate": True},
            ).to_dict()
        raise e
    except IntegrityError as e:
        return Response(
            data=None,
            message="Error: Verifique que el estudiante y la prueba existan",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error": str(e.orig)},
        ).to_dict()
    except Exception as e:
        return Response(
            data=None,
            message="Error al asignar prueba individual",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)},
        ).to_dict()


@router.post("/{test_id}/pay")
async def register_payment(session: SessionDep, test_id: int, request: PaymentRequest):
    try:
        app_service = RegisterTestPayment(session=session)
        data = await app_service.execute(test_id, request)
        return Response(
            data={
                "id": data.id,
                "estado": data.estado,
                "valor_pagado": data.valor_pagado,
            },
            message="Abono registrado exitosamente",
            status_code=status.HTTP_200_OK,
            details={"estado_actual": data.estado},
        ).to_dict()
    except Exception as e:
        return Response(
            data=None,
            message="Error al procesar pago",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)},
        ).to_dict()


@router.get("/student/{student_id}/status")
async def get_student_status(session: SessionDep, student_id: int):
    try:
        app_service = GetStudentTestStatus(session=session)
        data = await app_service.execute(student_id)
        return Response(
            data=data,
            message="Estado de pruebas consultado",
            status_code=status.HTTP_200_OK,
            details=data,
        ).to_dict()
    except Exception as e:
        return Response(
            data=None,
            message="Error al consultar estado",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)},
        ).to_dict()


@router.get("/details")
async def get_internal_tests(
    session: SessionDep,
    filter_pagination_query: Annotated[FilterPagination, Query()],
):
    try:
        tests_app = GetInternalTests(session=session)
        data = await tests_app.execute(filter_pagination=filter_pagination_query)

        return (
            Response(
                data=data,
                message="Pruebas obtenidas exitosamente",
                status_code=status.HTTP_200_OK,
                details={"message": "Pruebas obtenidas exitosamente"},
            )
            .filterPagination(
                page=filter_pagination_query.page,
                limit=filter_pagination_query.limit,
            )
            .to_dict()
        )
    except Exception as e:
        return Response(
            data=None,
            message="Error inesperado al obtener pruebas",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)},
        ).to_dict()


@router.get("/details/student/{student_id}")
async def get_internal_tests_by_student(
    session: SessionDep,
    student_id: int,
    filter_pagination_query: Annotated[FilterPagination, Query()],
):
    try:
        tests_app = GetInternalTestsByStudent(session=session)
        data = await tests_app.execute(
            student_id=student_id,
            filter_pagination=filter_pagination_query,
        )

        if not data:
            return Response(
                data=None,
                message="No se encontraron pruebas para el estudiante",
                status_code=status.HTTP_404_NOT_FOUND,
                details={"message": "No se encontraron pruebas para el estudiante"},
            ).to_dict()

        return (
            Response(
                data=data,
                message="Pruebas del estudiante obtenidas exitosamente",
                status_code=status.HTTP_200_OK,
                details={"message": "Pruebas del estudiante obtenidas exitosamente"},
            )
            .filterPagination(
                page=filter_pagination_query.page,
                limit=filter_pagination_query.limit,
            )
            .to_dict()
        )
    except Exception as e:
        return Response(
            data=None,
            message="Error inesperado al obtener pruebas del estudiante",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)},
        ).to_dict()


@router.get("/details/{test_id}")
async def get_internal_test_by_id(session: SessionDep, test_id: int):
    try:
        test_app = GetInternalTestById(session=session)
        data = await test_app.execute(test_id)

        if not data:
            return Response(
                data=None,
                message="Prueba no encontrada",
                status_code=status.HTTP_404_NOT_FOUND,
                details={"message": "Prueba no encontrada"},
            ).to_dict()

        return Response(
            data=data,
            message="Prueba obtenida exitosamente",
            status_code=status.HTTP_200_OK,
            details={"message": "Prueba obtenida exitosamente"},
        ).to_dict()
    except Exception as e:
        return Response(
            data=None,
            message="Error inesperado al obtener la prueba",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)},
        ).to_dict()


@router.post("/details")
async def create_internal_test(
    session: SessionDep,
    create_test_request: CreateTestDetailRequest,
):
    try:
        create_test_app = CreateInternalTest(session=session)
        data = await create_test_app.execute(create_test_request)

        if not data.id:
            return Response(
                data=None,
                message="Error al crear la prueba",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"message": "Error al crear la prueba"},
            ).to_dict()

        return Response(
            data=CreateTestDetailResponse(
                id=data.id,
                estudiante_id=data.estudiante_id,
                complementario_id=data.complementario_id,
                tipo_prueba=data.tipo_prueba,
                created_at=data.created_at,
                estado=data.estado,
            ),
            message="Prueba creada exitosamente",
            status_code=status.HTTP_201_CREATED,
            details={"message": "Prueba creada exitosamente"},
        ).to_dict()
    except IntegrityError as e:
        return Response(
            data=None,
            message="Error de integridad: Verifique que el estudiante y el complementario existan",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error": str(e.orig)},
        ).to_dict()
    except Exception as e:
        return Response(
            data=None,
            message="Error inesperado al crear la prueba",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)},
        ).to_dict()


@router.put("/details/{test_id}")
async def update_internal_test(
    session: SessionDep,
    test_id: int,
    update_test_request: UpdateTestDetailRequest,
):
    try:
        update_test_app = UpdateInternalTest(session=session)
        data = await update_test_app.execute(test_id, update_test_request)

        if not data:
            return Response(
                data=None,
                message="Error al actualizar la prueba o prueba no encontrada",
                status_code=status.HTTP_404_NOT_FOUND,
                details={
                    "message": "Error al actualizar la prueba o prueba no encontrada"
                },
            ).to_dict()

        if not data.id:
            return Response(
                data=None,
                message="Error al actualizar la prueba",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"message": "Error al actualizar la prueba"},
            ).to_dict()

        return Response(
            data=UpdateTestDetailResponse(
                id=data.id,
                estudiante_id=data.estudiante_id,
                complementario_id=data.complementario_id,
                tipo_prueba=data.tipo_prueba,
                created_at=data.created_at,
                estado=data.estado,
            ),
            message="Prueba actualizada exitosamente",
            status_code=status.HTTP_200_OK,
            details={"message": "Prueba actualizada exitosamente"},
        ).to_dict()
    except IntegrityError as e:
        return Response(
            data=None,
            message="Error de integridad: Verifique que el estudiante y el complementario existan",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error": str(e.orig)},
        ).to_dict()
    except Exception as e:
        return Response(
            data=None,
            message="Error inesperado al actualizar la prueba",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)},
        ).to_dict()


@router.delete("/details/{test_id}")
async def delete_internal_test(session: SessionDep, test_id: int):
    try:
        delete_app = DeleteInternalTest(session=session)
        await delete_app.execute(test_id)
        return Response(
            data={"id": test_id},
            message="Prueba eliminada exitosamente",
            status_code=status.HTTP_200_OK,
            details={"id": test_id},
        ).to_dict()
    except ValueError as e:
        return Response(
            data=None,
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND,
            details={"error": str(e)},
        ).to_dict()
    except Exception as e:
        return Response(
            data=None,
            message="Error al eliminar la prueba",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)},
        ).to_dict()


@router.put("/complementary/{comp_id}")
async def update_test_complementary(
    session: SessionDep,
    comp_id: int,
    body: ComplementaryUpdateBody,
):
    try:
        use_case = UpdateTestComplementary(session=session)
        await use_case.execute(
            comp_id=comp_id, tipo_complementario=body.nombre, valor=body.valor
        )
        return Response(
            data={"id": comp_id},
            message="Prueba actualizada exitosamente",
            status_code=status.HTTP_200_OK,
            details={"id": comp_id},
        ).to_dict()
    except ValueError as e:
        return Response(
            data=None,
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND,
            details={"error": str(e)},
        ).to_dict()
    except Exception as e:
        return Response(
            data=None,
            message="Error al actualizar la prueba",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)},
        ).to_dict()


@router.delete("/complementary/{comp_id}")
async def delete_test_complementary(session: SessionDep, comp_id: int):
    try:
        use_case = DeleteTestComplementary(session=session)
        await use_case.execute(comp_id=comp_id)
        return Response(
            data={"id": comp_id},
            message="Prueba eliminada exitosamente",
            status_code=status.HTTP_200_OK,
            details={"id": comp_id},
        ).to_dict()
    except ValueError as e:
        return Response(
            data=None,
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND,
            details={"error": str(e)},
        ).to_dict()
    except Exception as e:
        return Response(
            data=None,
            message="Error al eliminar la prueba",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)},
        ).to_dict()
