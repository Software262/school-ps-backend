from datetime import datetime

from sqlmodel import Field

from app.shared.infrastructure.base import Base

# Import external models to ensure SQLModel can resolve Foreign Keys


class ParametrizarPension(Base, table=True):
    grado_id: int = Field(foreign_key="grado.id")
    anio: int = Field()
    valor: int = Field()


class Pension(Base, table=True):
    para_pension_id: int = Field(foreign_key="parametrizarpension.id")
    estudiante_id: int = Field(foreign_key="estudiante.id")
    grado_id: int = Field(foreign_key="grado.id")
    valor_total: int = Field()
    fecha_registro: datetime = Field()
    estado_pension: bool = Field()


class DetallePension(Base, table=True):
    pension_id: int = Field(foreign_key="pension.id")
    estudiante_id: int = Field(foreign_key="estudiante.id")
    mes: int = Field()
    cuota: int = Field()
    valor_total: int = Field()
    valor_pagado: int = Field()
    fecha_pago: datetime = Field()
    faltante: bool = Field()
