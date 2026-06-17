from datetime import datetime

from pydantic import BaseModel


class ProgramResponse(BaseModel):
    id: int
    tipo_complementario: str
    anio: int
    valor: int
    estado_complemento: str


class StudentResponse(BaseModel):
    id: int
    nombre: str
    documento: str
    activo: bool


class PeriodResponse(BaseModel):
    id: int
    periodo_electivo: datetime
    estado: bool


class EnrollmentResponse(BaseModel):
    id: int
    complementario_id: int
    estudiante_id: int
    periodo_id: int | None
    usuario_id: int | None
    fecha_registro: datetime
    mes: str
    activo: bool
    estado_escuela: bool
    saldo_pendiente: int
    motivo_retiro: str | None
    created_at: datetime | None
    updated_at: datetime | None


class TipoComplementarioResponse(BaseModel):
    id: int
    nombre: str
    estado: bool
    sub_tipo_complementario: int | None
    padre_nombre: str | None


class ComplementarioResponse(BaseModel):
    id: int
    nombre: str
    anio: int
    valor: int
    estado_complemento: str
    tipo_complementario_id: int
    tipo_complementario_nombre: str


class EnrollmentDetailResponse(BaseModel):
    id: int
    complementario_id: int
    estudiante_id: int
    estudiante_nombre: str
    estudiante_documento: str
    estudiante_grado: str
    periodo_id: int | None
    usuario_id: int | None
    fecha_registro: datetime
    mes: str
    activo: bool
    estado_escuela: bool
    saldo_pendiente: int
    motivo_retiro: str | None
    observaciones: str | None
    valor_acordado: int
    numero_comprobante: str | None
    created_at: datetime | None
    updated_at: datetime | None
