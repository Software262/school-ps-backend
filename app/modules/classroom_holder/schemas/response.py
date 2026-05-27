from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.modules.classroom_holder.domain.enums import TipoIncidencia

class IncidenciaResponse(BaseModel):
    id: int
    estudiante_id: int
    docente_id: int
    tipo_incidencia: TipoIncidencia
    descripcion: str
    fecha: datetime
    esta_abierta: bool
    fecha_cierre: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PazYSalvoClassroomResponse(BaseModel):
    estudiante_id: int
    cumple_paz_y_salvo: bool
    mensaje: str