from datetime import datetime

from pydantic import BaseModel


class StudentEntity(BaseModel):
    id: int
    nombre: str
    activo: bool


class Borrowing(BaseModel):
    id: int | None
    nombre_articulo: str
    nombre_estudiante: str
    inventario_id: int
    estudiante_id: int
    fecha_salida: datetime
    fecha_devolucion: datetime | None
    estado_prestamo: bool
    cantidad: int
    observacion: str | None
    novedad_pendiente: bool = False


class StockState(BaseModel):
    estado: str
    cantidad: int


class GetInventoryItem(BaseModel):
    id: int
    tipo_inventario_id: int
    nombre: str
    cantidad_total: int
    observacion: str | None
    stocks: list[StockState]
