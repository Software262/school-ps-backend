from typing import Any, Literal

from pydantic import BaseModel, Field


class RunWebcolegiosImportRequest(BaseModel):
    url: str = Field(min_length=1)
    usuario: str = Field(min_length=1)
    contrasena: str = Field(min_length=1)


WebcolegiosManualLoadType = Literal["estudiante", "docente"]


class BulkWebcolegiosLoadRequest(BaseModel):
    tipo: WebcolegiosManualLoadType
    datos: list[dict[str, Any]] = Field(min_length=1)


class SingleWebcolegiosLoadRequest(BaseModel):
    tipo: WebcolegiosManualLoadType
    datos: dict[str, Any]
