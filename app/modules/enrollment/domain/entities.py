from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class StudentInfo:
    """Información básica del estudiante."""

    id: int
    nombre: str
    documento: str
    grado_id: int
    grado_nombre: str
    activo: bool


@dataclass
class ComplementaryDetail:
    """Detalle de un complementario dentro de la matrícula."""

    detalle_id: int = (
        0  # ID del registro en detallematricula (usar en PUT para descuentos)
    )
    complementario_id: int = 0
    tipo_complementario: str = ""
    valor: int = 0
    descuento: int = 0
    valor_completo: int = 0
    valor_pendiente: int = 0


@dataclass
class EnrollmentBalance:
    """Resultado consolidado del balance de matrícula de un estudiante."""

    student: StudentInfo
    year: int
    enrollment_base_cost: int
    complementary_items: list[ComplementaryDetail] = field(default_factory=list)
    complementary_total: int = 0
    total_cost: int = 0
    total_paid: int = 0
    total_pending: int = 0
    enrollment_status: str = "pendiente"
    enrollment_exists: bool = False
    pending_base: int = 0
    payments_count: int = 0
    matricula_id: int | None = None


@dataclass
class PaymentAllocation:
    """Cómo se distribuyó una parte del pago a un concepto."""

    concepto: str
    complementario_id: int | None
    monto_aplicado: int


@dataclass
class PaymentResult:
    """Resultado de procesar un pago."""

    pago_id: int
    codigo_talonario: str
    monto_total: int
    monto_aplicado: int
    distribuciones: list[PaymentAllocation]
    saldo_restante_matricula: int
    matricula_pagada: bool


@dataclass
class EnrollmentCreated:
    """Resultado de registrar una matrícula."""

    matricula_id: int
    estudiante_id: int
    valor_total: int
    costo_base: int
    total_complementarios: int
    complementarios: list[ComplementaryDetail]


@dataclass
class ComplementaryConcept:
    """Concepto complementario disponible en la institución."""

    id: int
    tipo_complementario: str
    anio: int
    valor: int
    estado_complemento: str


@dataclass
class StudentGeneralInfo:
    """Información general y resumida de un estudiante."""

    id: int
    nombre: str
    documento: str
    grado_nombre: str


@dataclass
class GradeInfo:
    """Información general de un grado."""

    id: int
    nombre: str


@dataclass
class PaymentHistoryItem:
    """Un pago dentro del historial de pagos de un estudiante."""

    id: int
    fecha_pago: datetime
    codigo_talonario: str
    monto_total: int
    observacion: str | None


@dataclass
class PaymentDistribution:
    """Distribución de un pago a un concepto específico."""

    concepto: str
    monto_aplicado: int


@dataclass
class PaymentReceipt:
    """Datos completos del comprobante de pago."""

    pago_id: int
    codigo_talonario: str
    fecha_pago: datetime
    monto_total: int
    observacion: str | None
    estudiante_id: int
    nombre_estudiante: str
    documento_estudiante: str
    grado_estudiante: str
    nombre_acudiente: str
    distribuciones: list[PaymentDistribution]
