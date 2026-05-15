from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


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
    id: Optional[int] = None


@dataclass
class TuitionAccount:
    para_pension_id: int
    estudiante_id: int
    grado_id: int
    valor_total: int
    fecha_registro: datetime
    estado_pension: bool
    id: Optional[int] = None
    installments: List[TuitionInstallment] = None
