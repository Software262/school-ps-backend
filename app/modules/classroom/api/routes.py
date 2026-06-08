from fastapi import APIRouter, status
from app.core.db import SessionDep
from app.modules.classroom.application.get_grades import GetGrades
from app.modules.classroom.application.get_pupitres_by_grade import GetPupitresByGrade
from app.modules.classroom.application.get_pupitre_by_student import GetPupitreByStudent
from app.modules.classroom.application.update_pupitre import UpdatePupitreState
from app.modules.classroom.application.bulk_update_pupitre import BulkUpdatePupitreState
from app.modules.classroom.schemas.request import (
    PupitreInSchema,
    BulkUpdateRequest,
)
from app.modules.classroom.schemas.response import (
    PupitreOutSchema,
    PupitreStudentOutSchema,
)
from app.shared.utils.response import Response
from app.modules.classroom.schemas.response import BulkUpdateResponse


router = APIRouter()


@router.get("/pupitre/grades")
async def get_grades(session: SessionDep):
    use_case = GetGrades(session)
    data = await use_case.execute()
    return Response(data=data, message="Lista de grados obtenida").to_dict()


# Se obtiene los pupitres asociados a los estudiantes que pertenecen a un mismo grado, si no se encuentran pupitres se retorna None
@router.get("/pupitre/grado/{grado_id}")
async def get_desks_by_grade(
    grado_id: int,
    session: SessionDep,
):
    use_case = GetPupitresByGrade(session=session)
    data = await use_case.execute(grado_id=grado_id)
    if not data:
        return Response(
            data=None,
            message="No se encontraron pupitres para el grado",
            status_code=status.HTTP_404_NOT_FOUND,
        ).to_dict()
    return Response(
        data=data,
        message="Pupitres obtenidos exitosamente",
        status_code=status.HTTP_200_OK,
    ).to_dict()


# Se obtiene el pupitre al cual pertenece el estudiante, si no tiene pupitre se retorna None
@router.get("/pupitre/{documento_estudiante}")
async def get_desk_by_student(
    documento_estudiante: str,
    session: SessionDep,
):
    use_case = GetPupitreByStudent(session=session)
    data = await use_case.execute(documento_estudiante=documento_estudiante)
    if not data:
        return Response(
            data=None,
            message="No se encontró el pupitre del estudiante",
            status_code=status.HTTP_404_NOT_FOUND,
        ).to_dict()
    return Response(
        data=PupitreStudentOutSchema(
            id=data.id,
            estudiante_id=data.estudiante_id,
            nombre_estudiante=data.nombre_estudiante,
            documento=data.documento,
            grado=data.grado,
            docente_titular=data.docente_titular,
            estado_pupitre=data.estado_pupitre,
            observacion=data.observacion,
        ),
        message="Pupitre obtenido exitosamente",
        status_code=status.HTTP_200_OK,
    ).to_dict()


# Se actualiza el estado de varios pupitres, se retorna la cantidad de pupitres actualizados
@router.patch("/pupitre/grado/{grado_id}")
async def bulk_update_desk_states(
    session: SessionDep,
    grado_id: int,
    request: BulkUpdateRequest,
):
    use_case = BulkUpdatePupitreState(session=session)
    data = await use_case.execute(grado_id=grado_id, request=request)

    if not data:
        return Response(
            data=None,
            message="No se encontraron pupitres para el grado",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"message": "No se encontraron pupitres para el grado"},
        ).to_dict()

    return Response(
        data=BulkUpdateResponse(total_actualizados=data["total_actualizados"]),
        message="Estado de pupitres actualizado exitosamente",
        status_code=status.HTTP_200_OK,
        details={"message": "Estado de pupitres actualizado exitosamente"},
    ).to_dict()


# Se actualiza el estado de UN pupitre, se retorna el pupitre actualizado
@router.patch("/pupitre/{estudiante_id}")
async def update_desk_state(
    session: SessionDep,
    estudiante_id: int,
    request: PupitreInSchema,
):
    use_case = UpdatePupitreState(session=session)
    data = await use_case.execute(estudiante_id=estudiante_id, request=request)

    if not data:
        return Response(
            data=None,
            message="No se encontró el pupitre del estudiante",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"message": "No se encontró el pupitre del estudiante"},
        ).to_dict()

    if not data.id:
        return Response(
            data=None,
            message="Error al actualizar el pupitre",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"message": "Error al actualizar el pupitre"},
        ).to_dict()

    return Response(
        data=PupitreOutSchema(
            id=data.id,
            estudiante_id=data.estudiante_id,
            estado_pupitre=data.estado_pupitre,
            observacion=data.observacion,
        ),
        message="Estado del pupitre actualizado exitosamente",
        status_code=status.HTTP_200_OK,
        details={"message": "Estado del pupitre actualizado exitosamente"},
    ).to_dict()
