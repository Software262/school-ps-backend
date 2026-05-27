from datetime import datetime

from pydantic import BaseModel


class EnrollmentResponse(BaseModel):
    id: int
    complementario_id: int
    estudiante_id: int
    estudiante_nombre: str | None = None
    estudiante_documento: str | None = None
    disciplina_nombre: str | None = None
    fecha_registro: datetime
    mes: str
    activo: bool
    estado_escuela: bool
    motivo_baja: str | None = None


class PaymentResponse(BaseModel):
    id: int
    complementario_id: int
    estudiante_id: int
    estudiante_nombre: str | None = None
    estudiante_documento: str | None = None
    disciplina_nombre: str | None = None
    mes: str
    estado_escuela: bool
    activo: bool
    updated_at: datetime


class GeneralStatusResponse(BaseModel):
    estudiante_id: int
    paz_y_salvo: bool
    detalle: str | None


class MonthlyStatusResponse(BaseModel):
    estudiante_id: int
    complementario_id: int
    paz_y_salvo: bool
    detalle: str
    meses: list[EnrollmentResponse]


class ProgramResponse(BaseModel):
    id: int
    nombre: str
    valor: int
    estado: str


class StudentResponse(BaseModel):
    id: int
    nombre: str
    documento: str
    activo: bool
