from pydantic import BaseModel, Field


class PupitreInSchema(BaseModel):
    estado_pupitre: bool
    observacion: str | None = Field(default=None, max_length=400)


class BulkUpdateRequest(BaseModel):
    estado_pupitre: bool
    observacion: str | None = Field(default=None, max_length=400)
