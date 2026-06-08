from fastapi import APIRouter, Depends, HTTPException, status
from app.core.db import SessionDep
from app.modules.classroom_holder.api.dependencies import verificar_acceso_salon_titular
from app.modules.classroom_holder.application.close_incident import CloseIncident
from app.modules.classroom_holder.application.create_incident import CreateIncident
from app.modules.classroom_holder.application.get_all_incidents import GetAllIncidents
from app.modules.classroom_holder.application.get_incidents_by_student import GetIncidentsByStudent
from app.modules.classroom_holder.application.search_students import SearchStudents
from app.modules.classroom_holder.application.verify_paz_y_salvo import VerifyPazYSalvo
from app.modules.classroom_holder.schemas.request import IncidenciaCreateRequest
from app.modules.classroom_holder.schemas.response import (
    EstudianteResumenResponse,
    IncidenciaResponse,
    PazYSalvoClassroomResponse,
)

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
    use_case = CreateIncident(session=session)
    return use_case.execute(payload, current_docente_id=current_user.id)


@router.get("/incidencias", response_model=list[IncidenciaResponse])
def listar_incidencias(session: SessionDep):
    use_case = GetAllIncidents(session=session)
    return use_case.execute()


@router.get(
    "/incidencias/estudiante/{estudiante_id}",
    response_model=list[IncidenciaResponse],
)
def listar_incidencias_por_estudiante(estudiante_id: int, session: SessionDep):
    use_case = GetIncidentsByStudent(session=session)
    return use_case.execute(estudiante_id)


@router.patch("/incidencias/{incidencia_id}/cerrar", response_model=IncidenciaResponse)
def cerrar_incidencia(incidencia_id: int, session: SessionDep):
    use_case = CloseIncident(session=session)
    resultado = use_case.execute(incidencia_id)
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró la incidencia con ID {incidencia_id}",
        )
    return resultado


@router.get(
    "/paz-y-salvo/verificar/{estudiante_id}",
    response_model=PazYSalvoClassroomResponse,
)
def verificar_paz_y_salvo(estudiante_id: int, session: SessionDep):
    use_case = VerifyPazYSalvo(session=session)
    cumple = use_case.execute(estudiante_id)
    mensaje = (
        "El estudiante se encuentra a paz y salvo en el Salón de Clases."
        if cumple
        else "Paz y salvo denegado: El estudiante presenta reportes abiertos en el Observador."
    )
    return PazYSalvoClassroomResponse(
        estudiante_id=estudiante_id, cumple_paz_y_salvo=cumple, mensaje=mensaje
    )


@router.get("/buscar-estudiantes", response_model=list[EstudianteResumenResponse])
def buscar_estudiantes(q: str, session: SessionDep):
    use_case = SearchStudents(session=session)
    return use_case.execute(q)
