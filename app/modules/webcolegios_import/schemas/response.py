from datetime import datetime

from pydantic import BaseModel


class ImportDetailResponse(BaseModel):
    tipo: str
    documento: str | None
    nombre: str | None
    estado: str
    observacion: str


class RunWebcolegiosImportResponse(BaseModel):
    total_estudiantes_scrapeados: int
    total_docentes_scrapeados: int
    estudiantes_insertados: int
    estudiantes_actualizados: int
    estudiantes_omitidos: int
    estudiantes_pendientes: int
    docentes_insertados: int
    docentes_omitidos: int
    errores: int
    detalle: list[ImportDetailResponse]


class WebcolegiosImportHistoryItem(BaseModel):
    id: int | None
    tipo_entidad: str
    documento_identidad: str
    nombre: str | None = None
    estado: str
    fecha_ingreso: datetime
    observacion: str


class WebcolegiosImportStatusResponse(BaseModel):
    total_registros: int
    ultimo_estado: str | None
    ultima_fecha: datetime | None
    recientes: list[WebcolegiosImportHistoryItem]


class ClearWebcolegiosImportResponse(BaseModel):
    deleted: int
    message: str
