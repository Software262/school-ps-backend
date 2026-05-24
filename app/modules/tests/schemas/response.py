from datetime import datetime

from pydantic import BaseModel


class CreateTestDetailResponse(BaseModel):
    id: int
    estudiante_id: int
    complementario_id: int
    tipo_prueba: str
    fecha_registro: datetime
    estado: bool


class UpdateTestDetailResponse(BaseModel):
    id: int
    estudiante_id: int
    complementario_id: int
    tipo_prueba: str
    fecha_registro: datetime
    estado: bool
