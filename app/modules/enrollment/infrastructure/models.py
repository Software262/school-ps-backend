from datetime import datetime

from sqlmodel import Field

from app.shared.infrastructure.base import Base


class Grado(Base, table=True):
    nombre: str = Field(max_length=50)


class Acudiente(Base, table=True):
    nombre: str = Field(max_length=50)
    parentesco: str = Field(max_length=20)
    telefono: str = Field(max_length=20)
    correo: str = Field(max_length=100)


class Estudiante(Base, table=True):
    grado_id: int = Field(foreign_key="grado.id")
    acudiente_id: int = Field(foreign_key="acudiente.id")
    nombre: str = Field(max_length=50)
    documento: str = Field(max_length=100)
    activo: bool = Field()
    fecha_activo: datetime | None = Field(default=None)


class Docente(Base, table=True):
    nombre: str = Field(max_length=50)
    documento: str = Field(max_length=20)
    estado: bool = Field(default=True)
    asignatura: str = Field(max_length=100)


class Periodo(Base, table=True):
    periodo_electivo: datetime
    estado: bool = Field(default=True)
    fecha: datetime = Field(nullable=False)


class Complementario(Base, table=True):
    tipo_complementario: str = Field(max_length=50)
    anio: int = Field(nullable=False)
    valor: int = Field()
    estado_complemento: str = Field(max_length=50)
    uso_matricula: bool = Field(default=False)


class ParametrizarMatricula(Base, table=True):
    grado_id: int = Field(foreign_key="grado.id")
    anio: int = Field()
    valor: int = Field()


class Matricula(Base, table=True):
    para_matricula_id: int = Field(foreign_key="parametrizarmatricula.id")
    estudiante_id: int = Field(foreign_key="estudiante.id")
    periodo_id: int = Field(foreign_key="periodo.id")
    valor_total: int = Field()
    fecha_registro: datetime = Field(nullable=False)
    estado_matricula: bool = Field()


class DetalleMatricula(Base, table=True):
    matricula_id: int = Field(foreign_key="matricula.id")
    complementario_id: int = Field(foreign_key="complementario.id")
    cuota: int = Field()
    descuento: int = Field()
    valor_completo: int = Field()
    valor_pendiente: int = Field()
    fecha_abono: datetime = Field()
