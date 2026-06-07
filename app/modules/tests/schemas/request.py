from pydantic import BaseModel, Field


class CreateTestDetailRequest(BaseModel):
    estudiante_id: int = Field(ge=1, description="ID del estudiante")
    complementario_id: int = Field(
        ge=1, description="ID del complementario asociado a la prueba"
    )
    tipo_prueba: str = Field(description="Tipo de prueba")
    estado: str = Field(default="pendiente", description="Estado del pago de la prueba")
    valor_pagado: int = Field(
        default=0, ge=0, description="Valor pagado hasta el momento"
    )
    periodo_id: int = Field(description="ID del periodo")


class UpdateTestDetailRequest(BaseModel):
    estudiante_id: int = Field(ge=1, description="ID del estudiante")
    complementario_id: int = Field(
        ge=1, description="ID del complementario asociado a la prueba"
    )
    tipo_prueba: str = Field(description="Tipo de prueba")
    estado: str = Field(description="Estado del pago de la prueba")
    valor_pagado: int = Field(
        default=0, ge=0, description="Valor pagado hasta el momento"
    )
    periodo_id: int = Field(description="ID del periodo")


class MassiveAssignmentRequest(BaseModel):
    grado_id: int
    complementario_id: int
    tipo_prueba: str
    periodo_id: int


class PaymentRequest(BaseModel):
    monto: int = Field(gt=0, description="Monto a abonar")


class ComplementaryUpdateBody(BaseModel):
    nombre: str
    valor: int
