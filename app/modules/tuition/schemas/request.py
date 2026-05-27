from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class PaymentCreateRequest(BaseModel):
    estudiante_id: int = Field(description="ID del estudiante")
    mes: int = Field(ge=1, le=12, description="Mes académico (1-12)")
    valor_pagado: int = Field(gt=0, description="Monto abonado en esta cuota")
    fecha_pago: datetime = Field(
        default_factory=datetime.now, description="Fecha de realización del pago"
    )

    @field_validator("valor_pagado")
    @classmethod
    def validate_valor_pagado(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("El valor del abono debe ser mayor a cero.")
        return v
