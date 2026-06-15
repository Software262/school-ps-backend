from pydantic import BaseModel, Field


class PupitreInSchema(BaseModel):
    observacion: str | None = Field(default=None, max_length=400)


class BulkUpdateRequest(BaseModel):
    estudiante_ids: list[int]
