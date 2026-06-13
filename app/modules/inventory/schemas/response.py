from pydantic import BaseModel


class StockStateResponse(BaseModel):
    estado: str
    cantidad: int


class GetInventoryItemResponse(BaseModel):
    id: int
    tipo_inventario_id: int
    nombre: str
    cantidad_total: int
    observacion: str | None
    stocks: list[StockStateResponse]


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
