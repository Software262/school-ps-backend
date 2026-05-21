from pydantic import BaseModel
from datetime import datetime


class CreateTypeInventoryResponse(BaseModel):
    id: int
    nombre: str


class CreateItemInventoryResponse(BaseModel):
    id: int
    nombre: str
    cantidad: int
    estado_objeto: str
    observacion: str | None


class UpdateItemInventoryResponse(BaseModel):
    id: int
    nombre: str
    cantidad: int
    estado_objeto: str
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


class BorrowingResponse(BaseModel):
    id: int
    inventario_id: int
    estudiante_id: int
    fecha_salida: datetime
    fecha_devolucion: datetime
    estado_prestamo: bool
    observacion: str | None = None
