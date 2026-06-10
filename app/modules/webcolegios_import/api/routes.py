import json
from typing import Any

from fastapi import APIRouter, Query, status

from app.core.db import SessionDep
from app.modules.webcolegios_import.application.bulk_webcolegios_load import (
    BulkWebcolegiosLoad,
)
from app.modules.webcolegios_import.application.reprocess_pending_students import (
    ReprocessPendingStudents,
)
from app.modules.webcolegios_import.application.run_import import RunWebcolegiosImport
from app.modules.webcolegios_import.application.run_import_students import (
    RunWebcolegiosImportStudents,
)
from app.modules.webcolegios_import.application.run_import_teachers import (
    RunWebcolegiosImportTeachers,
)
from app.modules.webcolegios_import.application.sync_staged_students import (
    SyncStagedStudents,
)
from app.modules.webcolegios_import.domain.entities import ImportSummary
from app.modules.webcolegios_import.infrastructure.repository import (
    WebcolegiosImportRepository,
)
from app.modules.webcolegios_import.schemas.request import (
    BulkWebcolegiosLoadRequest,
    RunWebcolegiosImportRequest,
    SingleWebcolegiosLoadRequest,
)
from app.modules.webcolegios_import.schemas.response import (
    ClearWebcolegiosImportResponse,
    ImportDetailResponse,
    RunWebcolegiosImportResponse,
    WebcolegiosImportHistoryItem,
    WebcolegiosImportStatusResponse,
)

router = APIRouter()


def _map_import_detail(item) -> ImportDetailResponse:
    return ImportDetailResponse(
        tipo=item.tipo,
        documento=item.documento,
        nombre=item.nombre,
        estado=item.estado,
        observacion=item.observacion,
    )


def _name_from_payload(payload: str) -> str | None:
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, dict):
        return None

    value = data.get("nombre")
    return str(value) if value else None


def _map_history_item(record: Any) -> WebcolegiosImportHistoryItem:
    return WebcolegiosImportHistoryItem(
        id=record.id,
        tipo_entidad=record.tipo_entidad,
        documento_identidad=record.documento_identidad,
        nombre=_name_from_payload(record.datos),
        estado=record.estado,
        fecha_ingreso=record.fecha_ingreso,
        observacion=record.observacion,
    )


def _map_summary(summary: ImportSummary) -> RunWebcolegiosImportResponse:
    return RunWebcolegiosImportResponse(
        total_estudiantes_scrapeados=summary.total_estudiantes_scrapeados,
        total_docentes_scrapeados=summary.total_docentes_scrapeados,
        estudiantes_insertados=summary.estudiantes_insertados,
        estudiantes_actualizados=summary.estudiantes_actualizados,
        estudiantes_omitidos=summary.estudiantes_omitidos,
        estudiantes_pendientes=summary.estudiantes_pendientes,
        docentes_insertados=summary.docentes_insertados,
        docentes_omitidos=summary.docentes_omitidos,
        errores=summary.errores,
        detalle=[_map_import_detail(item) for item in summary.detalle],
    )


@router.post(
    "/run",
    response_model=RunWebcolegiosImportResponse,
    status_code=status.HTTP_200_OK,
)
def run_webcolegios_import(
    session: SessionDep, request: RunWebcolegiosImportRequest
) -> RunWebcolegiosImportResponse:
    return _map_summary(RunWebcolegiosImport(session).execute(request))


@router.post(
    "/run/students",
    response_model=RunWebcolegiosImportResponse,
    status_code=status.HTTP_200_OK,
)
def run_webcolegios_students_import(
    session: SessionDep, request: RunWebcolegiosImportRequest
) -> RunWebcolegiosImportResponse:
    return _map_summary(RunWebcolegiosImportStudents(session).execute(request))


@router.post(
    "/run/teachers",
    response_model=RunWebcolegiosImportResponse,
    status_code=status.HTTP_200_OK,
)
def run_webcolegios_teachers_import(
    session: SessionDep, request: RunWebcolegiosImportRequest
) -> RunWebcolegiosImportResponse:
    return _map_summary(RunWebcolegiosImportTeachers(session).execute(request))


@router.post(
    "/carga-masiva",
    response_model=RunWebcolegiosImportResponse,
    status_code=status.HTTP_200_OK,
)
def bulk_load_webcolegios_import(
    session: SessionDep, request: BulkWebcolegiosLoadRequest
) -> RunWebcolegiosImportResponse:
    return _map_summary(BulkWebcolegiosLoad(session).execute(tipo=request.tipo, records=request.datos))


@router.post(
    "/carga-individual",
    response_model=RunWebcolegiosImportResponse,
    status_code=status.HTTP_200_OK,
)
def single_load_webcolegios_import(
    session: SessionDep, request: SingleWebcolegiosLoadRequest
) -> RunWebcolegiosImportResponse:
    return _map_summary(BulkWebcolegiosLoad(session).execute(tipo=request.tipo, records=[request.datos]))


@router.post(
    "/sincronizar-estudiantes",
    response_model=RunWebcolegiosImportResponse,
    status_code=status.HTTP_200_OK,
)
def sync_webcolegios_students(session: SessionDep) -> RunWebcolegiosImportResponse:
    return _map_summary(SyncStagedStudents(session).execute())


@router.post(
    "/reprocesar-pendientes-estudiantes",
    response_model=RunWebcolegiosImportResponse,
    status_code=status.HTTP_200_OK,
)
def reprocess_pending_webcolegios_students(
    session: SessionDep,
) -> RunWebcolegiosImportResponse:
    return _map_summary(ReprocessPendingStudents(session).execute())


@router.get("/history", response_model=list[WebcolegiosImportHistoryItem])
def get_webcolegios_import_history(
    session: SessionDep,
    limit: int = Query(default=50, ge=1, le=200),
) -> list[WebcolegiosImportHistoryItem]:
    repository = WebcolegiosImportRepository(session)
    return [_map_history_item(record) for record in repository.get_history(limit)]


@router.delete("/history", response_model=ClearWebcolegiosImportResponse)
def clear_webcolegios_import_history(
    session: SessionDep,
) -> ClearWebcolegiosImportResponse:
    repository = WebcolegiosImportRepository(session)
    deleted = repository.clear_history()
    return ClearWebcolegiosImportResponse(
        deleted=deleted,
        message="Historial de WebColegios eliminado.",
    )


@router.get("/errors", response_model=list[WebcolegiosImportHistoryItem])
def get_webcolegios_import_errors(
    session: SessionDep,
    limit: int = Query(default=50, ge=1, le=200),
) -> list[WebcolegiosImportHistoryItem]:
    repository = WebcolegiosImportRepository(session)
    return [_map_history_item(record) for record in repository.get_errors(limit)]


@router.delete("/errors", response_model=ClearWebcolegiosImportResponse)
def clear_webcolegios_import_errors(
    session: SessionDep,
) -> ClearWebcolegiosImportResponse:
    repository = WebcolegiosImportRepository(session)
    deleted = repository.clear_errors()
    return ClearWebcolegiosImportResponse(
        deleted=deleted,
        message="Errores y pendientes de WebColegios eliminados.",
    )


@router.get("/status", response_model=WebcolegiosImportStatusResponse)
def get_webcolegios_import_status(
    session: SessionDep,
) -> WebcolegiosImportStatusResponse:
    repository = WebcolegiosImportRepository(session)
    recent = repository.get_history(10)
    items = [_map_history_item(record) for record in recent]
    latest = items[0] if items else None
    return WebcolegiosImportStatusResponse(
        total_registros=len(items),
        ultimo_estado=latest.estado if latest else None,
        ultima_fecha=latest.fecha_ingreso if latest else None,
        recientes=items,
    )
