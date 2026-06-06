from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProgramInfo:
    id: int
    tipo_complementario: str
    anio: int
    valor: int
    estado_complemento: str
    uso_matricula: bool


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
