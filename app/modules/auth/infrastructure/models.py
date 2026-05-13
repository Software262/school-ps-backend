from datetime import datetime

from sqlmodel import Field

from app.shared.infrastructure.base import Base


class Actividad(Base, table=True):
    descripcion: str = Field(max_length=150)
    estado: bool = Field(default=True)
    fecha: datetime = Field(nullable=False)


class ImportacionAutomatica(Base, table=True):
    tipo_entidad: str = Field(max_length=20)
    documento_identidad: str = Field(max_length=50)
    datos: str = Field()
    estado: str = Field(max_length=20)
    fecha_ingreso: datetime = Field(nullable=False)
    observacion: str = Field()


class DetalleActividades(Base, table=True):
    usuario_id: int = Field(foreign_key="usuario.id")
    actividad_id: int = Field(foreign_key="actividad.id")


class Usuario(Base, table=True):
    rol: str = Field(max_length=50)
    username: str = Field(max_length=50)
    contrasenia: str = Field(max_length=255)
    estado: bool = Field(default=True)
