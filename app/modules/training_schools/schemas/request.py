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


class CreateTipoComplementarioRequest(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50)
    sub_tipo_complementario: int | None = Field(default=None, ge=1)


class UpdateTipoComplementarioRequest(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=50)
    estado: bool | None = Field(default=None)
    sub_tipo_complementario: int | None = Field(default=None, ge=1)


class CreateComplementarioRequest(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50)
    anio: int = Field(..., ge=2000)
    valor: int = Field(..., ge=0, le=2_147_483_647)
    estado_complemento: str = Field(..., min_length=1, max_length=50)
    tipo_complementario_id: int = Field(..., ge=1)


class UpdateComplementarioRequest(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=50)
    anio: int | None = Field(default=None, ge=2000)
    valor: int | None = Field(default=None, ge=0, le=2_147_483_647)
    estado_complemento: str | None = Field(default=None, min_length=1, max_length=50)
    tipo_complementario_id: int | None = Field(default=None, ge=1)
