from sqlmodel import Field

from app.shared.infrastructure.base import Base


class DetallePrueba(Base, table=True):
    estudiante_id: int = Field(foreign_key="estudiante.id")
    complementario_id: int = Field(foreign_key="complementario.id")
    tipo_prueba: str = Field(max_length=50)
    estado: str = Field(default="pendiente", max_length=20)
    valor_pagado: int = Field(default=0)
    periodo_id: int = Field(foreign_key="periodo.id")
