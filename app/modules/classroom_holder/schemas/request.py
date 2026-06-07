from datetime import datetime
from pydantic import BaseModel, Field
from app.modules.classroom_holder.domain.enums import TipoIncidencia


class IncidenciaCreateRequest(BaseModel):
    estudiante_id: int
    tipo_incidencia: TipoIncidencia
    descripcion: str = Field(..., max_length=400)
    fecha: datetime = Field(default_factory=datetime.utcnow)
