from sqlmodel import Field

from app.shared.infrastructure.base import Base


class WebcolegiosStagingStudent(Base, table=True):
    nombre: str | None = Field(default=None, max_length=150)
    documento: str | None = Field(default=None, max_length=100, index=True)
    grado_nombre: str | None = Field(default=None, max_length=100)
    curso: str | None = Field(default=None, max_length=50)
    sede: str | None = Field(default=None, max_length=100)
    jornada: str | None = Field(default=None, max_length=100)
    titular_nombre: str | None = Field(default=None, max_length=150)
    acudiente_nombre: str | None = Field(default=None, max_length=100)
    acudiente_telefono: str | None = Field(default=None, max_length=50)
    acudiente_correo: str | None = Field(default=None, max_length=150)
    raw_data: str = Field(default="")


class WebcolegiosStagingTeacher(Base, table=True):
    nombre: str | None = Field(default=None, max_length=150)
    documento: str | None = Field(default=None, max_length=100, index=True)
    asignatura: str | None = Field(default=None, max_length=100)
    grado_titular: str | None = Field(default=None, max_length=100)
    curso_titular: str | None = Field(default=None, max_length=50)
    sede: str | None = Field(default=None, max_length=100)
    jornada: str | None = Field(default=None, max_length=100)
    raw_data: str = Field(default="")
