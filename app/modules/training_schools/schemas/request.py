from pydantic import BaseModel, Field


class CreateEnrollmentRequest(BaseModel):
    estudiante_id: int = Field(
        ge=1, description="ID del estudiante a registrar en la escuela de formacion"
    )
    complementario_id: int = Field(
        ge=1, description="ID del programa complementario/escuela de formacion"
    )
    mes: str = Field(
        min_length=3,
        max_length=20,
        description="Mes correspondiente al registro mensual",
    )


class CreateProgramRequest(BaseModel):
    nombre: str = Field(
        min_length=3,
        max_length=50,
        description="Nombre de la disciplina o escuela de formacion",
    )
    valor: int = Field(
        ge=0,
        description="Valor administrativo asociado a la disciplina",
    )


class RegisterPaymentRequest(BaseModel):
    estudiante_id: int = Field(ge=1, description="ID del estudiante que paga el mes")
    complementario_id: int = Field(
        ge=1, description="ID del programa complementario/escuela de formacion"
    )
    mes: str = Field(
        min_length=3,
        max_length=20,
        description="Mes que se va a marcar como pagado",
    )


class UnsubscribeRequest(BaseModel):
    motivo: str = Field(
        min_length=5,
        max_length=255,
        description="Motivo por el cual se da de baja al estudiante del programa",
    )
