from dataclasses import dataclass
from datetime import datetime


@dataclass
class StudentSummary:
    nombre: str
    documento: str


@dataclass
class ComplementarySummary:
    tipo_complementario: str
    valor: int


@dataclass
class PeriodSummary:
    id: int
    nombre: str


@dataclass
class TestDetailEntity:
    id: int
    estudiante_id: int
    complementario_id: int
    tipo_prueba: str
    estado: str
    valor_pagado: int
    created_at: datetime | None
    estudiante: StudentSummary
    complementario: ComplementarySummary
    periodo_id: int | None = None
    periodo: PeriodSummary | None = None


@dataclass
class GradoEntity:
    id: int
    nombre: str


@dataclass
class PeriodoEntity:
    id: int
    nombre: str
    fecha: str


@dataclass
class EstudianteEntity:
    id: int
    nombre: str
    documento: str
    grado_id: int


@dataclass
class ComplementarioEntity:
    id: int
    tipo_complementario: str
    valor: int
    anio: int
