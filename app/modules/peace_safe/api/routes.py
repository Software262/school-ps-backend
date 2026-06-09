from fastapi import APIRouter, Query, status

from app.modules.peace_safe.application.generate_pazysalvo import (
    GenerateStudentPazYSalvo,
    GenerateTeacherPazYSalvo,
    GetPazYSalvoDetail,
)
from app.modules.peace_safe.application.get_student_status import (
    GetStudentStatus,
)
from app.modules.peace_safe.application.get_teacher_status import (
    GetTeacherStatus,
)
from app.modules.peace_safe.application.search_students import SearchStudents
from app.modules.peace_safe.application.search_teachers import SearchTeachers
from app.core.db import SessionDep
from app.shared.utils.response import Response

router = APIRouter()


@router.get("/search-students", status_code=status.HTTP_200_OK)
async def search_students(
    session: SessionDep,
    q: str = Query("", min_length=1, description="Nombre o documento del estudiante"),
):
    app_service = SearchStudents(session=session)
    result = await app_service.execute(q)
    return Response(
        data={"items": result},
        message="Estudiantes encontrados",
    ).to_dict()


@router.get("/search-teachers", status_code=status.HTTP_200_OK)
async def search_teachers(
    session: SessionDep,
    q: str = Query("", min_length=1, description="Nombre o documento del docente"),
):
    app_service = SearchTeachers(session=session)
    result = await app_service.execute(q)
    return Response(
        data={"items": result},
        message="Docentes encontrados",
    ).to_dict()


@router.get("/student/{estudiante_id}/status", status_code=status.HTTP_200_OK)
async def get_student_status(
    session: SessionDep,
    estudiante_id: int,
):
    app_service = GetStudentStatus(session=session)
    result = await app_service.execute(estudiante_id)
    if not result:
        return Response(
            data=None,
            message="Estudiante no encontrado",
            status_code=status.HTTP_404_NOT_FOUND,
        ).to_dict()
    return Response(
        data=result,
        message="Estado de paz y salvo del estudiante",
    ).to_dict()


@router.get("/teacher/{docente_id}/status", status_code=status.HTTP_200_OK)
async def get_teacher_status(
    session: SessionDep,
    docente_id: int,
):
    app_service = GetTeacherStatus(session=session)
    result = await app_service.execute(docente_id)
    if not result:
        return Response(
            data=None,
            message="Docente no encontrado",
            status_code=status.HTTP_404_NOT_FOUND,
        ).to_dict()
    return Response(
        data=result,
        message="Estado de paz y salvo del docente",
    ).to_dict()


@router.post("/student/{estudiante_id}/generate", status_code=status.HTTP_201_CREATED)
async def generate_student_pazysalvo(
    session: SessionDep,
    estudiante_id: int,
    usuario_id: int = Query(..., description="ID del usuario que genera"),
):
    app_service = GenerateStudentPazYSalvo(session=session)
    try:
        result = await app_service.execute(estudiante_id, usuario_id)
        if not result:
            return Response(
                data=None,
                message="Estudiante no encontrado",
                status_code=status.HTTP_404_NOT_FOUND,
            ).to_dict()
        return Response(
            data=result,
            message="Paz y salvo generado exitosamente",
        ).to_dict()
    except ValueError as e:
        return Response(
            data=None,
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        ).to_dict()


@router.post("/teacher/{docente_id}/generate", status_code=status.HTTP_201_CREATED)
async def generate_teacher_pazysalvo(
    session: SessionDep,
    docente_id: int,
    usuario_id: int = Query(..., description="ID del usuario que genera"),
):
    app_service = GenerateTeacherPazYSalvo(session=session)
    try:
        result = await app_service.execute(docente_id, usuario_id)
        if not result:
            return Response(
                data=None,
                message="Docente no encontrado",
                status_code=status.HTTP_404_NOT_FOUND,
            ).to_dict()
        return Response(
            data=result,
            message="Paz y salvo generado exitosamente",
        ).to_dict()
    except ValueError as e:
        return Response(
            data=None,
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
        ).to_dict()


@router.get("/{pazysalvo_id}", status_code=status.HTTP_200_OK)
async def get_pazysalvo_detail(
    session: SessionDep,
    pazysalvo_id: int,
):
    app_service = GetPazYSalvoDetail(session=session)
    result = await app_service.execute(pazysalvo_id)
    if not result:
        return Response(
            data=None,
            message="Paz y salvo no encontrado",
            status_code=status.HTTP_404_NOT_FOUND,
        ).to_dict()
    return Response(
        data=result,
        message="Detalle del paz y salvo",
    ).to_dict()
