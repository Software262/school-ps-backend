from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.db import SessionDep

from app.modules.classroom_holder.schemas.request import IncidenciaCreateRequest
from app.modules.classroom_holder.schemas.response import (
    IncidenciaResponse,
    PazYSalvoClassroomResponse,
)
from app.modules.classroom_holder.infrastructure.repository import IncidenciaRepository
from app.modules.classroom_holder.domain.service import ClassroomDomainService

from app.modules.classroom_holder.application.create_incident import (
    CreateIncidentUseCase,
)
from app.modules.classroom_holder.application.close_incident import CloseIncidentUseCase
from app.modules.classroom_holder.application.get_incidents import GetIncidentsUseCase

from app.modules.classroom_holder.api.dependencies import verificar_acceso_salon_titular

router = APIRouter(dependencies=[Depends(verificar_acceso_salon_titular)])


@router.post(
    "/incidencias",
    response_model=IncidenciaResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_incidencia(
    payload: IncidenciaCreateRequest,
    session: SessionDep,
    current_user=Depends(verificar_acceso_salon_titular),
):
    repo = IncidenciaRepository(session)
    use_case = CreateIncidentUseCase(repo)
    return use_case.execute(payload, current_docente_id=current_user.id)


@router.get(
    "/incidencias/estudiante/{estudiante_id}", response_model=List[IncidenciaResponse]
)
def listar_incidencias_por_estudiante(estudiante_id: int, session: SessionDep):
    repo = IncidenciaRepository(session)
    use_case = GetIncidentsUseCase(repo)
    return use_case.execute(estudiante_id)


@router.patch("/incidencias/{incidencia_id}/cerrar", response_model=IncidenciaResponse)
def cerrar_incidencia(incidencia_id: int, session: SessionDep):
    repo = IncidenciaRepository(session)
    use_case = CloseIncidentUseCase(repo)

    resultado = use_case.execute(incidencia_id)
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró la incidencia con ID {incidencia_id}",
        )
    return resultado


@router.get(
    "/paz-y-salvo/verificar/{estudiante_id}", response_model=PazYSalvoClassroomResponse
)
def verificar_paz_y_salvo(estudiante_id: int, session: SessionDep):
    repo = IncidenciaRepository(session)
    domain_service = ClassroomDomainService(repo)

    cumple = domain_service.verificar_paz_y_salvo(estudiante_id)
    mensaje = (
        "El estudiante se encuentra a paz y salvo en el Salón de Clases."
        if cumple
        else "Paz y salvo denegado: El estudiante presenta reportes abiertos en el Observador."
    )

    return PazYSalvoClassroomResponse(
        estudiante_id=estudiante_id, cumple_paz_y_salvo=cumple, mensaje=mensaje
    )


# 🌟 NUEVO ENDPOINT: Para el buscador del Frontend
@router.get("/buscar-estudiantes")
def buscar_estudiantes(q: str, session: SessionDep):
    repo = IncidenciaRepository(session)
    return repo.buscar_estudiantes_por_nombre(q)
