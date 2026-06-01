"""
Cafeteria Module API Endpoints.
This module handles the new operational flow:
1. List only active debtors.
2. Search general students to add new debts.
3. Bulk clear debts with predefined observations.

Author: Danilo Castillejo
Role: Developer of the cafeteria module
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from app.core.db import SessionDep

from app.modules.cafeteria.application.get_status import GetStatus
from app.modules.cafeteria.application.get_student_status import GetStudentStatus
from app.modules.cafeteria.application.create_observation import CreateObservation
from app.modules.cafeteria.application.update_status import UpdateStatus
from app.modules.cafeteria.application.export_report import ExportReport
from app.modules.cafeteria.application.search_general_students import (
    SearchGeneralStudents,
)


from app.modules.cafeteria.schemas.request import (
    ManualBlockRequest,
    BulkRemoveBlockRequest,
)
from app.shared.utils.response import Response

router = APIRouter()


@router.get("/list/{periodo_id}", summary="Obtener solo estudiantes con deuda activa")
async def get_debtors_list(periodo_id: int, session: SessionDep):
    """
    Retorna la lista de estudiantes registrados en la tabla de cafetería
    con 'estado_cafeteria' en False.
    """
    use_case = GetStatus(session)
    data = await use_case.execute(periodo_id)
    return Response(
        data=data,
        message="Lista de deudores activos obtenida exitosamente",
        status_code=status.HTTP_200_OK,
    ).to_dict()


@router.get("/search-students", summary="Buscar en la tabla general de estudiantes")
async def search_general_students(
    session: SessionDep,
    query: str | None = None,  # Ahora es opcional
    grado_id: int | None = None,  # Ahora es opcional
):
    """
    Busca estudiantes. Si no hay parámetros, devuelve los primeros 15.
    """
    use_case = SearchGeneralStudents(session)
    data = await use_case.execute(query, grado_id)
    return Response(
        data=data,
        message="Búsqueda general de estudiantes completada",
        status_code=status.HTTP_200_OK,
    ).to_dict()


@router.post("/add-debt", summary="Crear un nuevo registro de deuda para un estudiante")
async def add_debt(session: SessionDep, request: ManualBlockRequest):
    """
    Crea o actualiza un registro en la tabla de cafetería marcándolo como 'Deuda'.
    """
    use_case = CreateObservation(session)
    try:
        data = await use_case.execute(
            request.estudiante_id,
            request.periodo_id,
            request.usuario_id,
            request.observaciones,
        )
        return Response(
            data=data,
            message="Estudiante marcado como deudor exitosamente",
            status_code=status.HTTP_201_CREATED,
        ).to_dict()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/clear-debts", summary="Limpieza masiva de deudas (Pasar a Paz y Salvo)")
async def clear_debts(session: SessionDep, request: BulkRemoveBlockRequest):
    """
    Actualiza los registros seleccionados a 'Paz y Salvo' con una observación predefinida.
    """
    use_case = UpdateStatus(session)
    data = await use_case.execute(request.registro_ids, request.usuario_id)
    return Response(
        data=data,
        message="Los estudiantes seleccionados ahora están a Paz y Salvo",
        status_code=status.HTTP_200_OK,
    ).to_dict()


@router.get(
    "/status/{estudiante_id}/{periodo_id}", summary="Consultar estado individual"
)
async def get_individual_status(
    estudiante_id: int, periodo_id: int, session: SessionDep
):
    """
    Permite consultar el estado de un estudiante específico para un periodo dado.
    """
    use_case = GetStudentStatus(session)
    data = await use_case.execute(estudiante_id, periodo_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró registro para este estudiante",
        )
    return Response(
        data=data, message="Estado individual obtenido", status_code=status.HTTP_200_OK
    ).to_dict()


@router.get(
    "/export/{periodo_id}", summary="Descargar reporte CSV con info del estudiante"
)
async def export_csv(periodo_id: int, session: SessionDep):
    """
    Genera un reporte CSV con nombres, documentos y cursos mediante JOINs.
    """
    use_case = ExportReport(session)
    csv_content = await use_case.execute(periodo_id)
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=reporte_cafeteria_{periodo_id}.csv"
        },
    )


@router.get("/grades", summary="Obtener lista de grados reales")
async def get_grades(session: SessionDep):
    from app.modules.cafeteria.infrastructure.repository import CafeteriaRepository

    repo = CafeteriaRepository(session)
    grades = await repo.get_all_grades()
    return Response(data=grades).to_dict()
