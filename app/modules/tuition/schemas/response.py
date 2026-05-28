from datetime import datetime
from typing import List
from pydantic import BaseModel


class TuitionInstallmentResponse(BaseModel):
    id: int
    mes: int
    cuota: int
    valor_total: int
    valor_pagado: int
    total_pagado_mes: int
    saldo_pendiente: int
    fecha_pago: datetime | None = None
    faltante: bool


class TuitionAccountResponse(BaseModel):
    estudiante_id: int
    valor_total_anual: int
    estado_pension_general: bool
    installments: List[TuitionInstallmentResponse]
