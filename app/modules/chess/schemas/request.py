from pydantic import BaseModel, Field


class ReturnChessRequest(BaseModel):
    inventario_id: int = Field(ge=1, description="ID del tablero devuelto")
    estudiante_id: int = Field(ge=1, description="ID del estudiante")
    piezas_devueltas: int = Field(
        ge=0, le=32, description="Cantidad exacta de piezas devueltas (Max 32)"
    )
    reloj_funciona: bool = Field(description="¿El reloj funciona correctamente?")
    observacion: str = Field(description="Observación obligatoria en caso de novedad")
