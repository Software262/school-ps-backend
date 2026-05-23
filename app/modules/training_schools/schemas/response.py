from datetime import datetime
from pydantic import BaseModel


class EnrollmentResponse(BaseModel):
    id: int
    complementario_id: int
    estudiante_id: int
    fecha_registro: datetime
    mes: str
    activo: bool
    estado_escuela: bool
    motivo_baja: str | None = None


class PaymentResponse(BaseModel):
    id: int
    complementario_id: int
    estudiante_id: int
    mes: str
    estado_escuela: bool
    activo: bool
    updated_at: datetime


class GeneralStatusResponse(BaseModel):
    estudiante_id: int
    paz_y_salvo: bool
    detalle: str | None
