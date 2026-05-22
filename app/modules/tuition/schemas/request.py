from datetime import datetime
from pydantic import BaseModel, Field


class PaymentCreateRequest(BaseModel):
    estudiante_id: int = Field(description="ID del estudiante")
    mes: int = Field(ge=1, le=12, description="Mes académico (1-12)")
    valor_pagado: int = Field(gt=0, description="Monto abonado en esta cuota")
    fecha_pago: datetime = Field(
        default_factory=datetime.now, description="Fecha de realización del pago"
    )
