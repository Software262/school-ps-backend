from typing import Annotated

from fastapi import APIRouter, Query, status
from sqlalchemy.exc import IntegrityError

from app.core.db import SessionDep
from app.modules.tests.application.create_internal_test import CreateInternalTest
from app.modules.tests.application.get_internal_test_by_id import GetInternalTestById
from app.modules.tests.application.get_internal_tests import GetInternalTests
from app.modules.tests.application.get_internal_tests_by_student import (
    GetInternalTestsByStudent,
)
from app.modules.tests.application.update_internal_test import UpdateInternalTest
from app.modules.tests.schemas.request import (
    CreateTestDetailRequest,
    UpdateTestDetailRequest,
)
from app.modules.tests.schemas.response import (
    CreateTestDetailResponse,
    UpdateTestDetailResponse,
)
from app.shared.schemas.filter_pagination_request import FilterPagination
from app.shared.utils.response import Response

router = APIRouter()


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
