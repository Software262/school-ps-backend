from datetime import datetime

from pydantic import BaseModel


class PrincipalObservationResponse(BaseModel):
    id: int
    docente_id: int
    periodo_id: int
    descripcion: str
    tipo_observacion: str
    fecha: datetime


class PrincipalStatusResponse(BaseModel):
    id: int
    docente_id: int
    periodo_id: int
    motivo_estado: str
    fecha_actualizacion: datetime
