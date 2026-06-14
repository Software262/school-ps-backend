from datetime import datetime

from pydantic import BaseModel


class CreateTestDetailResponse(BaseModel):
    id: int
    estudiante_id: int
    complementario_id: int
    tipo_prueba: str
    created_at: datetime | None
    estado: str


class UpdateTestDetailResponse(BaseModel):
    id: int
    estudiante_id: int
    complementario_id: int
    tipo_prueba: str
    created_at: datetime | None
    estado: str
