from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProgramInfo:
    id: int
    tipo_complementario: str
    anio: int
    valor: int
    estado_complemento: str


@dataclass
class StudentInfo:
    id: int
    nombre: str
    documento: str
    activo: bool
    grado_nombre: str = ""


@dataclass
class PeriodInfo:
    id: int
    periodo_electivo: datetime
    estado: bool


@dataclass
class TipoComplementarioInfo:
    id: int
    nombre: str
    estado: bool
    sub_tipo_complementario: int | None = None
    padre_nombre: str | None = None


@dataclass
class ComplementarioInfo:
    id: int
    nombre: str
    anio: int
    valor: int
    estado_complemento: str
    tipo_complementario_id: int
    tipo_complementario_nombre: str = ""
