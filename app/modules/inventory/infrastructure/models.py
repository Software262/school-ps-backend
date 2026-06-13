from datetime import datetime

from sqlmodel import Field, UniqueConstraint

from app.shared.infrastructure.base import Base


class TipoInventario(Base, table=True):
    nombre: str = Field(unique=True, index=True, nullable=False, max_length=50)


class Inventario(Base, table=True):
    tipo_inventario_id: int = Field(foreign_key="tipoinventario.id")
    nombre: str = Field(nullable=False, max_length=50)
    cantidad_total: int = Field(nullable=False, default=0)
    observacion: str | None = Field(max_length=400)


class EstadoInventario(Base, table=True):
    nombre: str = Field(nullable=False, unique=True, max_length=50)


class InventarioStock(Base, table=True):
    inventario_id: int = Field(foreign_key="inventario.id")
    estado_inventario_id: int = Field(foreign_key="estadoinventario.id")
    cantidad: int = Field(ge=0, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "inventario_id", "estado_inventario_id", name="uq_inventario_estado"
        ),
    )


class Prestamo(Base, table=True):
    inventario_id: int = Field(foreign_key="inventario.id")
    estudiante_id: int = Field(foreign_key="estudiante.id")
    fecha_salida: datetime = Field(nullable=False)
    fecha_devolucion: datetime | None = Field(nullable=True)
    estado_prestamo: bool = Field(nullable=False)
    cantidad: int = Field(ge=1, nullable=False)
    observacion: str | None = Field(max_length=400)


class Novedad(Base, table=True):
    prestamo_id: int = Field(foreign_key="prestamo.id")
    descripcion: str = Field(nullable=False, max_length=250)
    resuelta: bool = Field(default=False)
