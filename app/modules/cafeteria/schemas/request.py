from pydantic import BaseModel, Field


class ManualBlockRequest(BaseModel):
    registro_id: int = Field(..., ge=1)
    usuario_id: int = Field(..., ge=1)
    observaciones: str = Field(..., min_length=5, max_length=400)


class BulkPazSalvoRequest(BaseModel):
    periodo_id: int = Field(..., ge=1)
    estudiantes_ids: list[int] = Field(..., min_length=1)  # Corrected
    usuario_id: int = Field(..., ge=1)


class BulkRemoveBlockRequest(BaseModel):
    registro_ids: list[int] = Field(..., min_length=1)  # Corrected
    usuario_id: int = Field(..., ge=1)
