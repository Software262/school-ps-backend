from pydantic import BaseModel, Field


class CreateEnrollmentRequest(BaseModel):
    estudiante_id: int = Field(
        ge=1, description="ID del estudiante a inscribir en la escuela de formación"
    )
    complementario_id: int = Field(
        ge=1, description="ID del programa complementario/escuela de formación"
    )
    mes: str = Field(
        min_length=3,
        max_length=20,
        description="Mes correspondiente a la inscripción (ej. Enero, Febrero, etc.)",
    )


class RegisterPaymentRequest(BaseModel):
    estudiante_id: int = Field(
        ge=1, description="ID del estudiante que realiza el pago"
    )
    complementario_id: int = Field(
        ge=1, description="ID del programa complementario/escuela de formación"
    )
    mes: str = Field(
        min_length=3,
        max_length=20,
        description="Mes que se va a pagar (ej. Enero, Febrero, etc.)",
    )


class UnsubscribeRequest(BaseModel):
    motivo: str = Field(
        min_length=5,
        max_length=255,
        description="Motivo por el cual se da de baja al estudiante del programa",
    )
