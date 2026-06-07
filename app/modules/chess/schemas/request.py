from datetime import datetime
from pydantic import BaseModel, Field, model_validator


class CreateChessBorrowRequest(BaseModel):
    inventario_id: int = Field(ge=1, description="ID del tablero a prestar")
    estudiante_id: int | None = Field(default=None, description="ID del estudiante")
    grado_id: int | None = Field(default=None, description="ID del grado")
    fecha_salida: datetime = Field(
        description="Fecha de préstamo", default_factory=datetime.now
    )
    cantidad: int = Field(default=1, ge=1, description="Cantidad de tableros")
    observacion: str | None = Field(None, description="Observación del préstamo")

    @model_validator(mode='after')
    def check_estudiante_or_grado(self) -> 'CreateChessBorrowRequest':
        if not self.estudiante_id and not self.grado_id:
            raise ValueError("Se debe especificar un estudiante_id o un grado_id")
        return self


class ReturnChessBorrowRequest(BaseModel):
    conteo_piezas: int = Field(ge=0, le=32, description="Número de piezas devueltas")
    observacion: str | None = Field(None, description="Observación al devolver")


class ResolveChessNoveltyRequest(BaseModel):
    notas_resolucion: str = Field(min_length=5, max_length=500, description="Detalles de la resolución")
    usuario_auditoria_id: int = Field(ge=1, description="ID del responsable que cierra la novedad")
