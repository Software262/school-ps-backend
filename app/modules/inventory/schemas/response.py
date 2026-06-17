from pydantic import BaseModel


class CreateTypeInventoryResponse(BaseModel):
    id: int
    nombre: str


class CreateItemInventoryResponse(BaseModel):
    id: int
    nombre: str
    cantidad_total: int
    observacion: str | None


class UpdateItemInventoryResponse(BaseModel):
    id: int
    nombre: str
    cantidad_total: int
    observacion: str | None


class CreateItemBorrowingResponse(BaseModel):
    id: int
    inventario_id: int
    estudiante_id: int
    cantidad: int
    estado_prestamo: bool
    observacion: str | None


class ReturnItemBorrowingResponse(BaseModel):
    id: int
    inventario_id: int
    estudiante_id: int
    cantidad: int
    estado_prestamo: bool
    observacion: str


class GetInventoryStatsResponse(BaseModel):
    total_items: int
    total_disponibles: int
    total_prestados: int
    total_mantenimiento: int


class ImportRowError(BaseModel):
    row: int
    nombre: str | None = None
    error: str


class ImportItemsResponse(BaseModel):
    total: int
    created: int
    updated: int
    failed: int
    errors: list[ImportRowError]
