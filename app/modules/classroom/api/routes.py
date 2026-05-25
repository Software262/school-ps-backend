from fastapi import APIRouter, status

from app.core.db import SessionDep
from app.modules.classroom.application.get_pupitres import GetPupitresByGrade
from app.modules.classroom.application.update_pupitre import UpdatePupitreState
from app.modules.classroom.application.bulk_update_pupitre import BulkUpdatePupitreState
from app.modules.classroom.schemas.request import (
    PupitreInSchema,
    BulkUpdateRequest,
)
from app.modules.classroom.schemas.response import PupitreOutSchema
from app.shared.utils.response import Response
from app.modules.classroom.schemas.response import BulkUpdateResponse


router = APIRouter()

@router.get("/pupitre/grado/{grado_id}")
async def obtener_pupitres_por_grado(
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
        data=[PupitreOutSchema(
            id=pupitre.id,
            estudiante_id=pupitre.estudiante_id,
            estado_pupitre=pupitre.estado_pupitre,
            observacion=pupitre.observacion
        ) for pupitre in data],
        message="Pupitres obtenidos exitosamente",
        status_code=status.HTTP_200_OK,
    ).to_dict()


@router.patch("/pupitre/grado/{grado_id}")
async def actualizar_estado_masivo(
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


@router.patch("/pupitre/{estudiante_id}")
async def actualizar_estado_pupitre(
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


