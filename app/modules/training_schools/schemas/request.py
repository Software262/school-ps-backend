from pydantic import BaseModel, Field


class EnrollStudentRequest(BaseModel):
    estudiante_id: int = Field(..., ge=1)
    complementario_id: int = Field(..., ge=1)
    periodo_id: int = Field(..., ge=1)
    mes: str = Field(..., min_length=1, max_length=20)
    usuario_id: int = Field(..., ge=1)
    observaciones: str | None = Field(default=None, max_length=400)
    # if not provided, defaults to program base price
    valor_acordado: int | None = Field(default=None, ge=0)
    numero_comprobante: str | None = Field(default=None, max_length=100)


class RegisterPaymentRequest(BaseModel):
    enrollment_id: int = Field(..., ge=1)
    monto: int = Field(..., ge=1)
    usuario_id: int = Field(..., ge=1)


class WithdrawStudentRequest(BaseModel):
    enrollment_id: int = Field(..., ge=1)
    motivo: str = Field(..., min_length=5, max_length=400)
    usuario_id: int = Field(..., ge=1)
