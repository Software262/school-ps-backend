"""
Cafeteria Module API Endpoints.
All business logic is delegated to the application layer (Use Cases).

Author: Danilo Castillejo
Role: Developer of the cafeteria module
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from app.core.db import SessionDep

# Use Cases
from app.modules.cafeteria.application.get_status import GetStatus
from app.modules.cafeteria.application.get_student_status import GetStudentStatus
from app.modules.cafeteria.application.create_observation import CreateObservation
from app.modules.cafeteria.application.update_status import UpdateStatus
from app.modules.cafeteria.application.remove_block import RemoveBlock
from app.modules.cafeteria.application.export_report import ExportReport

# Schemas
from app.modules.cafeteria.schemas.request import (
    ManualBlockRequest,
    BulkPazSalvoRequest,
    BulkRemoveBlockRequest,
)
from app.shared.utils.response import Response

router = APIRouter()


@router.get("/list/{periodo_id}", summary="Get all students status")
async def get_list(periodo_id: int, session: SessionDep):
    use_case = GetStatus(session)
    data = await use_case.execute(periodo_id)
    return Response(
        data=data, message="List obtained successfully", status_code=status.HTTP_200_OK
    ).to_dict()


@router.get(
    "/status/{estudiante_id}/{periodo_id}", summary="Get individual student status"
)
async def get_individual_status(
    estudiante_id: int, periodo_id: int, session: SessionDep
):
    use_case = GetStudentStatus(session)
    data = await use_case.execute(estudiante_id, periodo_id)
    if not data:
        raise HTTPException(status_code=404, detail="Record not found")
    return Response(
        data=data, message="Status obtained", status_code=status.HTTP_200_OK
    ).to_dict()


@router.post("/manual-block", summary="Mark student as debtor")
async def manual_block(session: SessionDep, request: ManualBlockRequest):
    use_case = CreateObservation(session)
    try:
        data = await use_case.execute(
            request.registro_id, request.usuario_id, request.observaciones
        )
        return Response(
            data=data,
            message="Manual block successful",
            status_code=status.HTTP_201_CREATED,
        ).to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/bulk-paz-y-salvo", summary="Massive Paz y Salvo assignment")
async def bulk_paz_y_salvo(session: SessionDep, request: BulkPazSalvoRequest):
    use_case = UpdateStatus(session)
    data = await use_case.execute(
        request.periodo_id, request.estudiantes_ids, request.usuario_id
    )
    return Response(
        data=data, message="Bulk operation completed", status_code=status.HTTP_200_OK
    ).to_dict()


@router.post("/remove-blocks", summary="Remove manual blocks in bulk")
async def remove_blocks(session: SessionDep, request: BulkRemoveBlockRequest):
    use_case = RemoveBlock(session)
    count = await use_case.execute(request.registro_ids, request.usuario_id)
    return Response(
        data={"updated": count},
        message="Blocks removed successfully",
        status_code=status.HTTP_200_OK,
    ).to_dict()


@router.get("/export/{periodo_id}", summary="Download CSV Report")
async def export_csv(periodo_id: int, session: SessionDep):
    use_case = ExportReport(session)
    csv_content = await use_case.execute(periodo_id)
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=report_cafeteria_{periodo_id}.csv"
        },
    )
