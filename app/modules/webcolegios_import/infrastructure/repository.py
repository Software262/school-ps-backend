import json
from datetime import datetime
from typing import Sequence

from sqlalchemy import and_, or_
from sqlmodel import Session, col, desc, select

from app.modules.auth.infrastructure.models import ImportacionAutomatica
from app.modules.enrollment.infrastructure.models import (
    Acudiente,
    Docente,
    Estudiante,
    Grado,
)
from app.modules.webcolegios_import.domain.entities import (
    ScrapedStudent,
    ScrapedTeacher,
)
from app.modules.webcolegios_import.domain.repositories import (
    WEBCOLEGIOS_ENTITY_TYPES,
    WEBCOLEGIOS_STUDENT_ENTITY,
    WebcolegiosImportRepository as WebcolegiosImportRepositoryInterface,
)
from app.modules.webcolegios_import.domain.service import (
    normalize_grade_key,
    normalize_grade_name,
    normalize_person_name,
    normalize_text,
    truncate,
)
from app.modules.webcolegios_import.infrastructure.models import (
    WebcolegiosStagingStudent,
    WebcolegiosStagingTeacher,
)

WEBCOLEGIOS_ERROR_STATES = ("ERROR", "PENDIENTE_DATOS")
DEFAULT_GUARDIAN_NAME = "N/A"
DEFAULT_GUARDIAN_RELATIONSHIP = "N/A"
DEFAULT_GUARDIAN_PHONE = "N/A"
DEFAULT_GUARDIAN_EMAIL = "na@webcolegios.local"


class WebcolegiosImportRepository(WebcolegiosImportRepositoryInterface):
    def __init__(self, session: Session):
        self.session = session

    def clear_staging(self) -> None:
        self.session.query(WebcolegiosStagingStudent).delete()
        self.session.query(WebcolegiosStagingTeacher).delete()
        self.session.commit()

    def save_staging_students(self, students: list[ScrapedStudent]) -> None:
        for student in students:
            self.session.add(
                WebcolegiosStagingStudent(
                    nombre=truncate(student.nombre, 150),
                    documento=truncate(student.documento, 100),
                    grado_nombre=truncate(student.grado_nombre, 100),
                    curso=truncate(student.curso, 50),
                    sede=truncate(student.sede, 100),
                    jornada=truncate(student.jornada, 100),
                    titular_nombre=truncate(student.titular_nombre, 150),
                    acudiente_nombre=truncate(student.acudiente_nombre, 100),
                    acudiente_telefono=truncate(student.acudiente_telefono, 50),
                    acudiente_correo=truncate(student.acudiente_correo, 150),
                    raw_data=json.dumps(student.raw_data, ensure_ascii=False),
                )
            )
        self.session.commit()

    def save_staging_teachers(self, teachers: list[ScrapedTeacher]) -> None:
        for teacher in teachers:
            self.session.add(
                WebcolegiosStagingTeacher(
                    nombre=truncate(teacher.nombre, 150),
                    documento=truncate(teacher.documento, 100),
                    asignatura=truncate(teacher.asignatura, 100),
                    grado_titular=truncate(teacher.grado_titular, 100),
                    curso_titular=truncate(teacher.curso_titular, 50),
                    sede=truncate(teacher.sede, 100),
                    jornada=truncate(teacher.jornada, 100),
                    raw_data=json.dumps(teacher.raw_data, ensure_ascii=False),
                )
            )
        self.session.commit()

    def get_staging_students(self) -> list[ScrapedStudent]:
        rows = self.session.exec(select(WebcolegiosStagingStudent)).all()
        return [
            ScrapedStudent(
                nombre=row.nombre or "",
                documento=row.documento or "",
                grado_nombre=row.grado_nombre,
                curso=row.curso,
                sede=row.sede,
                jornada=row.jornada,
                titular_nombre=row.titular_nombre,
                acudiente_nombre=row.acudiente_nombre,
                acudiente_telefono=row.acudiente_telefono,
                acudiente_correo=row.acudiente_correo,
                raw_data=json.loads(row.raw_data) if row.raw_data else {},
            )
            for row in rows
        ]

    def get_staging_teachers(self) -> list[ScrapedTeacher]:
        rows = self.session.exec(select(WebcolegiosStagingTeacher)).all()
        return [
            ScrapedTeacher(
                nombre=row.nombre or "",
                documento=row.documento or "",
                asignatura=row.asignatura,
                grado_titular=row.grado_titular,
                curso_titular=row.curso_titular,
                sede=row.sede,
                jornada=row.jornada,
                raw_data=json.loads(row.raw_data) if row.raw_data else {},
            )
            for row in rows
        ]

    def find_student_by_document(self, document: str) -> Estudiante | None:
        return self.session.exec(
            select(Estudiante).where(col(Estudiante.documento) == document)
        ).first()

    def find_teacher_by_document(self, document: str) -> Docente | None:
        return self.session.exec(
            select(Docente).where(col(Docente.documento) == document)
        ).first()

    def find_teacher_by_name(self, name: str | None) -> Docente | None:
        normalized = normalize_person_name(name)
        if not normalized:
            return None

        teachers = self.session.exec(select(Docente)).all()
        return next(
            (
                teacher
                for teacher in teachers
                if normalize_person_name(teacher.nombre) == normalized
            ),
            None,
        )

    def find_grade_by_name(self, name: str | None) -> Grado | None:
        grade_name = normalize_grade_name(name)
        normalized = normalize_grade_key(grade_name)
        if not normalized:
            return None

        grades = self.session.exec(select(Grado)).all()
        return next(
            (
                grade
                for grade in grades
                if normalize_grade_key(grade.nombre) == normalized
            ),
            None,
        )

    def get_or_create_grade_by_name(self, grade_name: str | None) -> Grado | None:
        normalized_name = normalize_grade_name(grade_name)
        if not normalized_name:
            return None

        existing = self.find_grade_by_name(normalized_name)
        if existing:
            return existing

        grade = Grado(nombre=truncate(normalized_name, 50))
        self.session.add(grade)
        self.session.commit()
        self.session.refresh(grade)
        return grade

    def find_guardian(
        self, name: str | None, phone: str | None, email: str | None
    ) -> Acudiente | None:
        normalized_name = normalize_text(name)
        normalized_phone = normalize_text(phone)
        normalized_email = normalize_text(email)

        if not any((normalized_name, normalized_phone, normalized_email)):
            return None

        guardians = self.session.exec(select(Acudiente)).all()
        for guardian in guardians:
            matches_name = (
                normalized_name and normalize_text(guardian.nombre) == normalized_name
            )
            matches_phone = (
                normalized_phone
                and normalize_text(guardian.telefono) == normalized_phone
            )
            matches_email = (
                normalized_email and normalize_text(guardian.correo) == normalized_email
            )

            if matches_email or (
                matches_name and (matches_phone or not normalized_phone)
            ):
                return guardian

        return None

    def get_or_create_default_guardian_na(self) -> Acudiente:
        guardian = self.session.exec(
            select(Acudiente).where(col(Acudiente.nombre) == DEFAULT_GUARDIAN_NAME)
        ).first()
        if guardian:
            return guardian

        guardian = Acudiente(
            nombre=DEFAULT_GUARDIAN_NAME,
            parentesco=DEFAULT_GUARDIAN_RELATIONSHIP,
            telefono=DEFAULT_GUARDIAN_PHONE,
            correo=DEFAULT_GUARDIAN_EMAIL,
        )
        self.session.add(guardian)
        self.session.commit()
        self.session.refresh(guardian)
        return guardian

    def get_or_create_guardian(
        self, name: str | None, phone: str | None, email: str | None
    ) -> Acudiente:
        normalized_name = normalize_text(name)
        normalized_phone = normalize_text(phone)
        normalized_email = normalize_text(email)

        if not any((normalized_name, normalized_phone, normalized_email)):
            return self.get_or_create_default_guardian_na()

        existing = self.find_guardian(name, phone, email)
        if existing:
            return existing

        guardian = Acudiente(
            nombre=truncate(name or "ACUDIENTE SIN NOMBRE", 50),
            parentesco="ACUDIENTE",
            telefono=truncate(phone or DEFAULT_GUARDIAN_PHONE, 20),
            correo=truncate(email or "sin-correo@webcolegios.local", 100),
        )
        self.session.add(guardian)
        self.session.commit()
        self.session.refresh(guardian)
        return guardian

    def is_default_guardian(self, guardian_id: int | None) -> bool:
        if guardian_id is None:
            return False

        guardian = self.session.get(Acudiente, guardian_id)
        return bool(guardian and guardian.nombre == DEFAULT_GUARDIAN_NAME)

    def update_student_guardian(
        self, student: Estudiante, guardian_id: int
    ) -> Estudiante:
        student.acudiente_id = guardian_id
        student.updated_at = datetime.now()
        self.session.add(student)
        self.session.commit()
        self.session.refresh(student)
        return student

    def update_student_grade(self, student: Estudiante, grade_id: int) -> Estudiante:
        student.grado_id = grade_id
        student.updated_at = datetime.now()
        self.session.add(student)
        self.session.commit()
        self.session.refresh(student)
        return student

    def create_student(
        self, nombre: str, documento: str, grado_id: int, acudiente_id: int
    ) -> Estudiante:
        student = Estudiante(
            grado_id=grado_id,
            acudiente_id=acudiente_id,
            nombre=truncate(nombre, 50),
            documento=truncate(documento, 100),
            activo=True,
            fecha_activo=datetime.now(),
        )
        self.session.add(student)
        self.session.commit()
        self.session.refresh(student)
        return student

    def create_teacher(self, nombre: str, documento: str, asignatura: str) -> Docente:
        teacher = Docente(
            nombre=truncate(nombre, 50),
            documento=truncate(documento, 20),
            estado=True,
            asignatura=truncate(asignatura or "SIN ASIGNATURA", 100),
        )
        self.session.add(teacher)
        self.session.commit()
        self.session.refresh(teacher)
        return teacher

    def register_import_result(
        self,
        tipo_entidad: str,
        documento_identidad: str,
        datos: str,
        estado: str,
        observacion: str,
    ) -> ImportacionAutomatica:
        record = ImportacionAutomatica(
            tipo_entidad=tipo_entidad,
            documento_identidad=truncate(documento_identidad, 50),
            datos=datos,
            estado=estado,
            fecha_ingreso=datetime.now(),
            observacion=observacion,
        )
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def update_import_result_status(
        self,
        record: ImportacionAutomatica,
        estado: str,
        observacion: str,
    ) -> ImportacionAutomatica:
        record.estado = truncate(estado, 20)
        record.observacion = observacion
        record.updated_at = datetime.now()
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def get_history(self, limit: int) -> Sequence[ImportacionAutomatica]:
        return self.session.exec(
            select(ImportacionAutomatica)
            .where(
                col(ImportacionAutomatica.tipo_entidad).in_(WEBCOLEGIOS_ENTITY_TYPES)
            )
            .order_by(desc(ImportacionAutomatica.fecha_ingreso))
            .limit(limit)
        ).all()

    def get_errors(self, limit: int) -> Sequence[ImportacionAutomatica]:
        return self.session.exec(
            select(ImportacionAutomatica)
            .where(
                col(ImportacionAutomatica.tipo_entidad).in_(WEBCOLEGIOS_ENTITY_TYPES),
                col(ImportacionAutomatica.estado).in_(WEBCOLEGIOS_ERROR_STATES),
            )
            .order_by(desc(ImportacionAutomatica.fecha_ingreso))
            .limit(limit)
        ).all()

    def get_pending_student_imports(self) -> Sequence[ImportacionAutomatica]:
        return self.session.exec(
            select(ImportacionAutomatica)
            .where(
                col(ImportacionAutomatica.tipo_entidad) == WEBCOLEGIOS_STUDENT_ENTITY,
                or_(
                    col(ImportacionAutomatica.estado) == "PENDIENTE_DATOS",
                    and_(
                        col(ImportacionAutomatica.estado) == "INSERTADO",
                        col(ImportacionAutomatica.observacion).like(
                            "Pendiente reprocesado.%"
                        ),
                    ),
                ),
            )
            .order_by(col(ImportacionAutomatica.id))
        ).all()

    def clear_history(self) -> int:
        deleted = (
            self.session.query(ImportacionAutomatica)
            .filter(
                col(ImportacionAutomatica.tipo_entidad).in_(WEBCOLEGIOS_ENTITY_TYPES)
            )
            .delete(synchronize_session=False)
        )
        self.session.commit()
        return int(deleted)

    def clear_errors(self) -> int:
        deleted = (
            self.session.query(ImportacionAutomatica)
            .filter(
                col(ImportacionAutomatica.tipo_entidad).in_(WEBCOLEGIOS_ENTITY_TYPES),
                col(ImportacionAutomatica.estado).in_(WEBCOLEGIOS_ERROR_STATES),
            )
            .delete(synchronize_session=False)
        )
        self.session.commit()
        return int(deleted)
