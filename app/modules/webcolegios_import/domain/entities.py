from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ScrapedStudent:
    nombre: str
    documento: str
    grado_nombre: str | None = None
    curso: str | None = None
    sede: str | None = None
    jornada: str | None = None
    titular_nombre: str | None = None
    acudiente_nombre: str | None = None
    acudiente_telefono: str | None = None
    acudiente_correo: str | None = None
    raw_data: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ScrapedTeacher:
    nombre: str
    documento: str
    asignatura: str | None = None
    grado_titular: str | None = None
    curso_titular: str | None = None
    sede: str | None = None
    jornada: str | None = None
    raw_data: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class WebcolegiosScrapeResult:
    students: list[ScrapedStudent]
    teachers: list[ScrapedTeacher]


@dataclass(slots=True)
class ImportDetail:
    tipo: str
    documento: str | None
    nombre: str | None
    estado: str
    observacion: str


@dataclass(slots=True)
class ImportSummary:
    total_estudiantes_scrapeados: int = 0
    total_docentes_scrapeados: int = 0
    estudiantes_insertados: int = 0
    estudiantes_actualizados: int = 0
    estudiantes_omitidos: int = 0
    estudiantes_pendientes: int = 0
    docentes_insertados: int = 0
    docentes_omitidos: int = 0
    errores: int = 0
    detalle: list[ImportDetail] = field(default_factory=list)
