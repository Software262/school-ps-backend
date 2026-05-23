from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TuitionInstallment:
    pension_id: int
    estudiante_id: int
    mes: int
    cuota: int
    valor_total: int
    valor_pagado: int
    fecha_pago: datetime
    faltante: bool
    id: int | None = None


@dataclass
class TuitionAccount:
    para_pension_id: int
    estudiante_id: int
    grado_id: int
    valor_total: int
    fecha_registro: datetime
    estado_pension: bool
    id: int | None = None
    installments: list[TuitionInstallment] = field(default_factory=list)
