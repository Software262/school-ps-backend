from datetime import datetime

from sqlmodel import Field

from app.shared.infrastructure.base import Base

# Import external models to ensure SQLModel can resolve Foreign Keys


class ParametrizarPension(Base, table=True):
    grado_id: int = Field(foreign_key="grado.id", nullable=False)
    anio: int = Field(nullable=False)
    valor: int = Field(nullable=False)


class Pension(Base, table=True):
    para_pension_id: int = Field(foreign_key="parametrizarpension.id", nullable=False)
    estudiante_id: int = Field(foreign_key="estudiante.id", nullable=False)
    grado_id: int = Field(foreign_key="grado.id", nullable=False)
    valor_total: int = Field(nullable=False)
    fecha_registro: datetime = Field(nullable=False)
    estado_pension: bool = Field(nullable=False)


class DetallePension(Base, table=True):
    pension_id: int = Field(foreign_key="pension.id", nullable=False)
    estudiante_id: int = Field(foreign_key="estudiante.id", nullable=False)
    mes: int = Field(nullable=False)
    cuota: int = Field(nullable=False)
    valor_total: int = Field(nullable=False)
    valor_pagado: int = Field(nullable=False)
    fecha_pago: datetime = Field(nullable=False)
    faltante: bool = Field(nullable=False)
