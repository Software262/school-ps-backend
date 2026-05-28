from enum import Enum

from pydantic import BaseModel, Field


class TipoPruebaEnum(str, Enum):
    simulacro = "simulacro"
    saber = "saber"
    icfes = "icfes"


class CreateTestDetailRequest(BaseModel):
    estudiante_id: int = Field(
        ge=1,
        description="ID del estudiante",
    )
    complementario_id: int = Field(
        ge=1,
        description="ID del complementario asociado a la prueba",
    )
    tipo_prueba: TipoPruebaEnum = Field(
        description="Tipo de prueba (simulacro, saber, icfes)",
    )
    estado: bool = Field(
        default=False,
        description="Estado del pago de la prueba",
    )


class UpdateTestDetailRequest(BaseModel):
    estudiante_id: int = Field(
        ge=1,
        description="ID del estudiante",
    )
    complementario_id: int = Field(
        ge=1,
        description="ID del complementario asociado a la prueba",
    )
    tipo_prueba: TipoPruebaEnum = Field(
        description="Tipo de prueba (simulacro, saber, icfes)",
    )
    estado: bool = Field(
        description="Estado del pago de la prueba",
    )
