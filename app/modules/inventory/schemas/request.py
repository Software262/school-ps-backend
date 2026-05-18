from datetime import datetime

from pydantic import BaseModel, Field


class CreateTypeInventoryRequest(BaseModel):
    nombre: str = Field(
        min_length=2, max_length=80, description="Nombre del tipo de inventario"
    )


class CreateItemRequest(BaseModel):
    tipo_inventario_id: int = Field(
        ge=1, description="ID del tipo de inventario al que pertenece el item"
    )
    nombre: str = Field(min_length=2, max_length=100, description="Nombre del item")
    cantidad: int = Field(ge=1, description="Cantidad del item")
    estado_objeto: str = Field(
        min_length=2, max_length=100, description="Estado del objeto"
    )
    observacion: str | None = Field(None, description="Observación del item")


class UpdateItemRequest(BaseModel):
    tipo_inventario_id: int = Field(
        ge=1, description="ID del tipo de inventario al que pertenece el item"
    )
    nombre: str = Field(min_length=2, max_length=100, description="Nombre del item")
    cantidad: int = Field(ge=0, description="Cantidad del item")
    estado_objeto: str = Field(
        min_length=2, max_length=100, description="Estado del objeto"
    )
    observacion: str | None = Field(None, description="Observación del item")


class CreateBorrowRequest(BaseModel):
    inventario_id: int = Field(ge=1, description="ID del item a prestar")
    estudiante_id: int = Field(
        ge=1, description="ID del estudiante que presta el articulo"
    )
    fecha_salida: datetime = Field(
        description="Fecha de préstamo en formato YYYY-MM-DD", examples=[datetime.now()]
    )
    cantidad: int = Field(ge=1, description="Cantidad del articulo a prestar")
    estado_prestamo: bool = Field(description="Estado del préstamo")
    observacion: str | None = Field(None, description="Observación del préstamo")
