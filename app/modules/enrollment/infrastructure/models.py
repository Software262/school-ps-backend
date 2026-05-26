from datetime import datetime

from sqlmodel import Field

from app.shared.infrastructure.base import Base


class Grado(Base, table=True):
    """Grados académicos de la institución."""

    nombre: str = Field(max_length=50)


class Acudiente(Base, table=True):
    """Acudiente (tutor/representante) del estudiante."""

    nombre: str = Field(max_length=50)
    parentesco: str = Field(max_length=20)
    telefono: str = Field(max_length=20)
    correo: str = Field(max_length=100)


class Estudiante(Base, table=True):
    """Estudiante matriculado en la institución."""

    grado_id: int = Field(foreign_key="grado.id")
    acudiente_id: int = Field(foreign_key="acudiente.id")
    nombre: str = Field(max_length=50)
    documento: str = Field(max_length=100)
    activo: bool = Field(default=True)
    fecha_activo: datetime | None = Field(default=None)


class Docente(Base, table=True):
    nombre: str = Field(max_length=50)
    documento: str = Field(max_length=20)
    estado: bool = Field(default=True)
    asignatura: str = Field(max_length=100)


class Periodo(Base, table=True):
    """Periodo electivo académico."""

    periodo_electivo: datetime
    estado: bool = Field(default=True)
    fecha: datetime = Field(nullable=False)


class Complementario(Base, table=True):
    """Cobro complementario que puede aplicarse a la matrícula."""

    tipo_complementario: str = Field(max_length=50)
    anio: int = Field(nullable=False)
    valor: int = Field()
    estado_complemento: str = Field(max_length=50)
    uso_matricula: bool = Field(default=False)


class ParametrizarMatricula(Base, table=True):
    """Configuración del costo base de matrícula por grado y año."""

    grado_id: int = Field(foreign_key="grado.id")
    anio: int = Field()
    valor: int = Field()


class Matricula(Base, table=True):
    """Registro de matrícula de un estudiante."""

    para_matricula_id: int = Field(foreign_key="parametrizarmatricula.id")
    estudiante_id: int = Field(foreign_key="estudiante.id")
    periodo_id: int = Field(foreign_key="periodo.id")
    valor_total: int = Field()
    fecha_registro: datetime = Field(nullable=False)
    estado_matricula: str = Field(default="sin_abono", max_length=20)
    valor_pendiente_base: int = Field(default=0)


class DetalleMatricula(Base, table=True):
    """Detalle de un ítem de la matrícula (complementario asignado)."""

    matricula_id: int = Field(foreign_key="matricula.id")
    complementario_id: int = Field(foreign_key="complementario.id")
    cuota: int = Field()
    descuento: int = Field()
    valor_completo: int = Field()
    valor_pendiente: int = Field()
    fecha_abono: datetime = Field()


class Pago(Base, table=True):
    """Registro de un pago realizado sobre la matrícula."""

    matricula_id: int = Field(foreign_key="matricula.id")
    codigo_talonario: str = Field(max_length=50, unique=True)
    monto_total: int = Field()
    fecha_pago: datetime = Field(default_factory=datetime.now)
    observacion: str | None = Field(default=None, max_length=255)


class PagoDetalle(Base, table=True):
    """Desglose de un pago: cuánto se aplicó a cada concepto."""

    pago_id: int = Field(foreign_key="pago.id")
    concepto: str = Field(max_length=50)
    complementario_id: int | None = Field(default=None, foreign_key="complementario.id")
    monto_aplicado: int = Field()
