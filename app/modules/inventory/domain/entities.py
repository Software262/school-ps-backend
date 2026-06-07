from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel


@dataclass
class StudentEntity:
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
