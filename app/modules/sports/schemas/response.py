from datetime import datetime

from pydantic import BaseModel


class SportItemResponse(BaseModel):
    id: int | None
    nombre: str
    cantidad: int
    estado_objeto: str
    observacion: str | None


class SportBorrowResponse(BaseModel):
    id: int | None
    inventario_id: int
    estudiante_id: int
    cantidad: int
    estado_prestamo: bool
    fecha_salida: datetime
    fecha_devolucion: datetime | None
    observacion: str | None


class ReturnSportBorrowResponse(BaseModel):
    id: int | None
    inventario_id: int
    estudiante_id: int
    cantidad: int
    estado_prestamo: bool
    fecha_devolucion: datetime | None
    observacion: str | None


class SportNovedadResponse(BaseModel):
    id: int | None
    prestamo_id: int
    descripcion: str
    resuelta: bool


class PazYSalvoStatusResponse(BaseModel):
    """Estado de paz y salvo del módulo de deportes para un estudiante."""

    estudiante_id: int
    tiene_prestamos_activos: bool
    tiene_novedades_abiertas: bool
    paz_y_salvo: bool
    detalle: str
