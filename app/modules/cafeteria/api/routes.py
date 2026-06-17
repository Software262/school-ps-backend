"""
Cafeteria Module API Endpoints.

Author: Danilo Castillejo
Role: Developer of the cafeteria module
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from app.core.db import SessionDep
from app.shared.utils.response import Response

from app.modules.cafeteria.application.get_status import GetStatus
from app.modules.cafeteria.application.get_grades import GetGrades
from app.modules.cafeteria.application.export_report import ExportReport
from app.modules.cafeteria.application.search_general_students import (
    SearchGeneralStudents,
)
from app.modules.cafeteria.application.create_observation import CreateObservation
from app.modules.cafeteria.application.update_status import UpdateStatus
from app.modules.cafeteria.application.get_student_status import GetStudentStatus
from app.modules.cafeteria.schemas.request import (
    ManualBlockRequest,
    BulkRemoveBlockRequest,
)

router = APIRouter()


@router.get("/list/{periodo_id}")
async def get_debtors_list(periodo_id: int, session: SessionDep):
    use_case = GetStatus(session)
    data = await use_case.execute(periodo_id)
    return Response(data=data, message="Deudores activos obtenidos").to_dict()


@router.get("/search-students")
async def search_students(
    session: SessionDep, query: str | None = None, grado_id: int | None = None
):
    use_case = SearchGeneralStudents(session)
    data = await use_case.execute(query, grado_id)
    return Response(data=data, message="Búsqueda completada").to_dict()


@router.get("/grades")
async def get_grades(session: SessionDep):
    use_case = GetGrades(session)
    data = await use_case.execute()
    return Response(data=data, message="Lista de grados obtenida").to_dict()


@router.post("/add-debt")
async def add_debt(session: SessionDep, request: ManualBlockRequest):
    use_case = CreateObservation(session)
    try:
        data = await use_case.execute(
            request.estudiante_id,
            request.periodo_id,
            request.usuario_id,
            request.observaciones,
        )
        return Response(
            data=data, message="Deuda registrada", status_code=status.HTTP_201_CREATED
        ).to_dict()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/clear-debts")
async def clear_debts(session: SessionDep, request: BulkRemoveBlockRequest):
    use_case = UpdateStatus(session)
    data = await use_case.execute(request.registro_ids, request.usuario_id)
    return Response(data=data, message="Deudas limpiadas").to_dict()


@router.get("/status/{estudiante_id}/{periodo_id}")
async def get_individual_status(
    estudiante_id: int, periodo_id: int, session: SessionDep
):
    use_case = GetStudentStatus(session)
    data = await use_case.execute(estudiante_id, periodo_id)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Registro no encontrado"
        )
    return Response(data=data, message="Estado obtenido").to_dict()


@router.get("/export/{periodo_id}")
async def export_pdf(periodo_id: int, session: SessionDep):
    use_case = ExportReport(session)
    pdf_content = await use_case.execute(periodo_id)
    return StreamingResponse(
        iter([pdf_content]),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=reporte_{periodo_id}.pdf"
        },
    )
