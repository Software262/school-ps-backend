from datetime import datetime

from sqlmodel import Field

from app.shared.infrastructure.base import Base


class TipoInventario(Base, table=True):
    nombre: str = Field(unique=True, index=True, nullable=False, max_length=50)


class Inventario(Base, table=True):
    tipo_inventario_id: int = Field(foreign_key="tipoinventario.id")
    nombre: str = Field(nullable=False, max_length=50)
    cantidad: int = Field(nullable=False)
    estado_objeto: str = Field(nullable=False, max_length=50)
    observacion: str | None = Field(max_length=400)


class Prestamo(Base, table=True):
    inventario_id: int = Field(foreign_key="inventario.id")
    estudiante_id: int = Field(foreign_key="estudiante.id")
    fecha_salida: datetime = Field(nullable=False)
    fecha_devolucion: datetime = Field(nullable=False)
    estado_prestamo: bool = Field(nullable=False)
    observacion: str | None = Field(max_length=400)
