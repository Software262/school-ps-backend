from datetime import datetime

from sqlmodel import Field

from app.shared.infrastructure.base import Base


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
    detalle_matricula_id: int = Field(foreign_key="detallematricula.id")
    mes: int = Field()
