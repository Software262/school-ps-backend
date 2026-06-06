from datetime import datetime

from pydantic import BaseModel


class ComplementaryItemResponse(BaseModel):
    """DTO para un ítem complementario dentro de la matrícula."""

    detalle_id: int
    complementario_id: int
    tipo_complementario: str
    valor: int
    descuento: int
    valor_completo: int
    valor_pendiente: int


class StudentInfoResponse(BaseModel):
    """DTO con información básica del estudiante."""

    id: int
    nombre: str
    documento: str
    grado_id: int
    grado_nombre: str
    activo: bool


class EnrollmentBalanceResponse(BaseModel):
    """DTO de respuesta con el balance completo de matrícula."""

    estudiante: StudentInfoResponse
    anio: int
    costo_base_matricula: int
    complementarios: list[ComplementaryItemResponse]
    total_complementarios: int
    costo_total: int
    total_pagado: int
    total_pendiente: int
    estado_matricula: str  # sin_abono | parcial | paz_y_salvo
    matricula_registrada: bool
    pendiente_base: int
    pagos_realizados: int
    matricula_id: int | None = None


class EnrollmentCreatedResponse(BaseModel):
    """Respuesta al crear una matrícula."""

    matricula_id: int
    estudiante_id: int
    valor_total: int
    costo_base: int
    total_complementarios: int
    complementarios: list[ComplementaryItemResponse]
    mensaje: str


class PaymentDistributionResponse(BaseModel):
    """Detalle de cómo se distribuyó un pago a un concepto."""

    concepto: str
    complementario_id: int | None = None
    monto_aplicado: int


class PaymentResultResponse(BaseModel):
    """Respuesta al registrar un pago."""

    pago_id: int
    codigo_talonario: str
    monto_total: int
    monto_aplicado: int
    distribuciones: list[PaymentDistributionResponse]
    saldo_restante: int
    matricula_pagada: bool
    mensaje: str


class StudentSearchItemResponse(BaseModel):
    """DTO de respuesta individual para la búsqueda de estudiantes."""

    estudiante_id: int
    documento: str
    nombre: str
    grado_id: int
    grado_nombre: str
    anio: int
    matricula_registrada: bool
    estado_matricula: str  # sin_abono | parcial | paz_y_salvo | sin_matricula
    pagos_realizados: int
    saldo_pendiente: int
    costo_total: int
    total_pagado: int


class StudentSearchListResponse(BaseModel):
    """DTO de respuesta de listado para la búsqueda de estudiantes."""

    estudiantes: list[StudentSearchItemResponse]
    total_resultados: int


class PaymentHistoryItemResponse(BaseModel):
    """DTO para un ítem del historial de pagos (auditoría)."""

    id: int
    codigo_talonario: str
    monto_total: int
    fecha_pago: datetime
    observacion: str | None = None


class StudentReceiptInfo(BaseModel):
    """DTO de estudiante para el comprobante."""

    id: int
    nombre: str
    documento: str
    grado: str


class AcudienteReceiptInfo(BaseModel):
    """DTO de acudiente para el comprobante."""

    nombre: str


class PaymentReceiptResponse(BaseModel):
    """DTO completo del comprobante de pago."""

    pago_id: int
    codigo_talonario: str
    monto_total: int
    fecha_pago: datetime
    observacion: str | None = None
    estudiante: StudentReceiptInfo
    acudiente: AcudienteReceiptInfo
    distribuciones: list[PaymentDistributionResponse]


class StudentResponse(BaseModel):
    grado_id: int
    acudiente_id: int
    nombre: str
    documento: str
    activo: bool
    fecha_activo: datetime | None


class GradeResponse(BaseModel):
    id: int
    nombre: str


class StudentGeneralResponse(BaseModel):
    id: int
    nombre: str
    documento: str
    grado_nombre: str
