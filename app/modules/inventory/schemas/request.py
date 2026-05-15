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
    cantidad: int = Field(ge=0, description="Cantidad del item")
    estado_objeto: str = Field(
        min_length=2, max_length=100, description="Estado del objeto"
    )
    observacion: str | None = Field(None, description="Observación del item")
