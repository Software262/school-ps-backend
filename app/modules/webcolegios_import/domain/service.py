import json
import re
import unicodedata

from app.modules.webcolegios_import.domain.entities import (
    ImportDetail,
    ImportSummary,
    ScrapedStudent,
    ScrapedTeacher,
)
from app.modules.webcolegios_import.domain.repositories import (
    WEBCOLEGIOS_STUDENT_ENTITY,
    WEBCOLEGIOS_TEACHER_ENTITY,
    WebcolegiosImportRepository,
)


def clean_text(value: str | None) -> str:
    return " ".join((value or "").strip().split())


def normalize_text(value: str | None) -> str:
    cleaned = clean_text(value).lower()
    return "".join(
        char
        for char in unicodedata.normalize("NFD", cleaned)
        if unicodedata.category(char) != "Mn"
    )


def normalize_grade_key(value: str | None) -> str:
    normalized = normalize_text(value)
    return re.sub(r"[^a-z0-9]", "", normalized)


def normalize_person_name(value: str | None) -> str:
    normalized = normalize_text(value)
    return re.sub(r"[^a-z0-9]", "", normalized)


WEBCOLEGIOS_GRADE_ALIASES = {
    "parvulos": "Párvulos",
    "prejardin": "Prejardín",
    "jardin": "Jardín",
    "transicion": "Transición",
    "jardindetransicion": "Jardín de Transición",
    "septimo": "Séptimo",
    "decimo": "Décimo",
}

INVALID_GRADE_KEYS = {"", "na"}


def normalize_grade_name(value: str | None) -> str:
    cleaned = clean_text(value)
    if not cleaned:
        return ""

    key = normalize_grade_key(cleaned)
    if key in INVALID_GRADE_KEYS:
        return ""

    mapped = WEBCOLEGIOS_GRADE_ALIASES.get(key)
    if mapped:
        return mapped

    normalized_words = re.sub(r"[-_]+", " ", cleaned)
    normalized_words = re.sub(r"[^A-Za-z0-9À-ſ\s]", "", normalized_words)
    return " ".join(word.capitalize() for word in normalized_words.split())


def normalize_document(value: str | None) -> str:
    return "".join(char for char in (value or "") if char.isdigit()).strip()


def truncate(value: str | None, max_length: int) -> str:
    return clean_text(value)[:max_length]


DEFAULT_GUARDIAN_NAME = "N/A"


class WebcolegiosImportService:
    def __init__(self, repository: WebcolegiosImportRepository) -> None:
        self.repository = repository

    def clear_staging(self) -> None:
        self.repository.clear_staging()

    def sync_students(self, summary: ImportSummary) -> ImportSummary:
        for student in self.repository.get_staging_students():
            self._sync_student(student, summary)
        return summary

    def sync_teachers(self, summary: ImportSummary) -> ImportSummary:
        for teacher in self.repository.get_staging_teachers():
            self._sync_teacher(teacher, summary)
        return summary

    def _sync_student(self, student: ScrapedStudent, summary: ImportSummary) -> None:
        document = normalize_document(student.documento)
        name = clean_text(student.nombre)
        has_real_guardian = self._has_real_guardian_data(student)

        try:
            if not document or not name:
                self._register_student(
                    summary,
                    student,
                    "ERROR",
                    "Documento o nombre vacío en el registro scrapeado.",
                )
                summary.errores += 1
                return

            grade = self.repository.get_or_create_grade_by_name(student.grado_nombre)
            if not grade or grade.id is None:
                self._register_student(
                    summary,
                    student,
                    "PENDIENTE_DATOS",
                    self._build_missing_grade_observation(student),
                )
                summary.estudiantes_pendientes += 1
                return

            existing_student = self.repository.find_student_by_document(document)
            if existing_student:
                updates = []
                if existing_student.grado_id != grade.id:
                    existing_student = self.repository.update_student_grade(
                        existing_student, grade.id
                    )
                    updates.append(f"grado actualizado a '{grade.nombre}'")

                if has_real_guardian and self.repository.is_default_guardian(
                    existing_student.acudiente_id
                ):
                    guardian = self.repository.get_or_create_guardian(
                        student.acudiente_nombre,
                        student.acudiente_telefono,
                        student.acudiente_correo,
                    )
                    if guardian.id is None:
                        raise ValueError("No se pudo resolver el acudiente real.")
                    existing_student = self.repository.update_student_guardian(
                        existing_student, guardian.id
                    )
                    updates.append("acudiente real actualizado")

                if updates:
                    self._register_student(
                        summary,
                        student,
                        "ACTUALIZADO",
                        f"Estudiante existente actualizado: {', '.join(updates)}.",
                    )
                    summary.estudiantes_actualizados += 1
                    return

                observation = (
                    "El estudiante ya existe y conserva su acudiente actual."
                    if has_real_guardian
                    else "El estudiante ya existe en la tabla estudiante."
                )
                self._register_student(
                    summary, student, "OMITIDO_EXISTENTE", observation
                )
                summary.estudiantes_omitidos += 1
                return

            guardian = (
                self.repository.get_or_create_guardian(
                    student.acudiente_nombre,
                    student.acudiente_telefono,
                    student.acudiente_correo,
                )
                if has_real_guardian
                else self.repository.get_or_create_default_guardian_na()
            )
            if guardian.id is None:
                raise ValueError("No se pudo resolver el acudiente.")

            self.repository.create_student(
                nombre=name,
                documento=document,
                grado_id=grade.id,
                acudiente_id=guardian.id,
            )
            self._register_student(
                summary,
                student,
                "INSERTADO",
                "Estudiante insertado desde WebColegios."
                if has_real_guardian
                else "Estudiante insertado con acudiente N/A temporal.",
            )
            summary.estudiantes_insertados += 1
        except Exception as exc:
            self._register_student(
                summary, student, "ERROR", f"Error al sincronizar: {exc}"
            )
            summary.errores += 1

    def _sync_teacher(self, teacher: ScrapedTeacher, summary: ImportSummary) -> None:
        document = normalize_document(teacher.documento)
        name = clean_text(teacher.nombre)
        subject = clean_text(teacher.asignatura) or "SIN ASIGNATURA"

        try:
            if not name:
                self._register_teacher(
                    summary, teacher, "ERROR", "Nombre vacio en el registro scrapeado."
                )
                summary.errores += 1
                return

            existing_by_name = self.repository.find_teacher_by_name(name)
            existing_document = (
                normalize_document(existing_by_name.documento)
                if existing_by_name
                else ""
            )
            if existing_by_name and existing_document:
                teacher.documento = existing_document
                self._register_teacher(
                    summary,
                    teacher,
                    "OMITIDO_EXISTENTE",
                    "El docente titular ya existe en la tabla docente.",
                )
                summary.docentes_omitidos += 1
                return

            if not document:
                self._register_teacher(
                    summary,
                    teacher,
                    "PENDIENTE_DATOS",
                    self._build_missing_document_observation(teacher, name),
                )
                return

            if self.repository.find_teacher_by_document(document):
                self._register_teacher(
                    summary,
                    teacher,
                    "OMITIDO_EXISTENTE",
                    "El docente ya existe en la tabla docente.",
                )
                summary.docentes_omitidos += 1
                return

            self.repository.create_teacher(name, document, subject)
            self._register_teacher(
                summary, teacher, "INSERTADO", "Docente insertado desde WebColegios."
            )
            summary.docentes_insertados += 1
        except Exception as exc:
            self._register_teacher(
                summary, teacher, "ERROR", f"Error al sincronizar: {exc}"
            )
            summary.errores += 1

    def _has_real_guardian_data(self, student: ScrapedStudent) -> bool:
        values = (
            student.acudiente_nombre,
            student.acudiente_telefono,
            student.acudiente_correo,
        )
        return any(
            clean_text(v) and clean_text(v).upper() != DEFAULT_GUARDIAN_NAME
            for v in values
        )

    def _build_missing_grade_observation(self, student: ScrapedStudent) -> str:
        grade_webcolegios = clean_text(student.grado_nombre)
        grade_normalized = normalize_grade_name(grade_webcolegios)
        if not grade_normalized:
            return "No se pudo resolver grado. grado_webcolegios vacío o inválido."
        return (
            "No se pudo resolver grado. "
            f"grado_webcolegios='{grade_webcolegios}', "
            f"grado_normalizado='{grade_normalized}', "
            f"curso='{clean_text(student.curso)}'"
        )

    def _build_missing_document_observation(
        self, teacher: ScrapedTeacher, name: str
    ) -> str:
        return (
            "No se pudo resolver documento del titular. "
            f"titular_nombre='{name}', "
            f"grado='{clean_text(teacher.grado_titular)}', "
            f"curso='{clean_text(teacher.curso_titular)}'"
        )

    def _register_student(
        self,
        summary: ImportSummary,
        student: ScrapedStudent,
        estado: str,
        observacion: str,
    ) -> None:
        document = normalize_document(student.documento)
        name = clean_text(student.nombre)
        payload = {
            "nombre": name,
            "documento": document,
            "grado_nombre": student.grado_nombre,
            "grado_normalizado": normalize_grade_name(student.grado_nombre),
            "curso": student.curso,
            "sede": student.sede,
            "jornada": student.jornada,
            "titular_nombre": student.titular_nombre,
            "acudiente_nombre": student.acudiente_nombre,
        }
        self.repository.register_import_result(
            tipo_entidad=WEBCOLEGIOS_STUDENT_ENTITY,
            documento_identidad=document,
            datos=json.dumps(payload, ensure_ascii=False),
            estado=estado,
            observacion=observacion,
        )
        summary.detalle.append(
            ImportDetail(
                tipo="estudiante",
                documento=document,
                nombre=name,
                estado=estado,
                observacion=observacion,
            )
        )

    def _register_teacher(
        self,
        summary: ImportSummary,
        teacher: ScrapedTeacher,
        estado: str,
        observacion: str,
    ) -> None:
        document = normalize_document(teacher.documento)
        name = clean_text(teacher.nombre)
        payload = {
            "nombre": name,
            "documento": document,
            "asignatura": clean_text(teacher.asignatura) or "SIN ASIGNATURA",
            "grado_titular": teacher.grado_titular,
            "curso_titular": teacher.curso_titular,
            "sede": teacher.sede,
            "jornada": teacher.jornada,
        }
        self.repository.register_import_result(
            tipo_entidad=WEBCOLEGIOS_TEACHER_ENTITY,
            documento_identidad=document,
            datos=json.dumps(payload, ensure_ascii=False),
            estado=estado,
            observacion=observacion,
        )
        summary.detalle.append(
            ImportDetail(
                tipo="docente",
                documento=document,
                nombre=name,
                estado=estado,
                observacion=observacion,
            )
        )
