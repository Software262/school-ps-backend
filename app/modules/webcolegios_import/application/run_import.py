from app.core.logger import setup_logger
from app.modules.webcolegios_import.application.clean_temp_tables import (
    CleanWebcolegiosTempTables,
)
from app.modules.webcolegios_import.application.sync_students import SyncStudents
from app.modules.webcolegios_import.application.sync_teachers import SyncTeachers
from app.modules.webcolegios_import.domain.entities import ImportDetail, ImportSummary
from app.modules.webcolegios_import.domain.repositories import (
    WebcolegiosImportRepository,
)
from app.modules.webcolegios_import.infrastructure.scraper_adapter import (
    WebcolegiosScraperAdapter,
)
from app.modules.webcolegios_import.infrastructure.repository import (
    WEBCOLEGIOS_SYSTEM_ENTITY,
)
from app.modules.webcolegios_import.schemas.request import RunWebcolegiosImportRequest

logger = setup_logger()


def _mask_user(usuario: str) -> str:
    cleaned = usuario.strip()
    if not cleaned:
        return ""
    if len(cleaned) <= 2:
        return f"{cleaned[0]}***"
    return f"{cleaned[:2]}***{cleaned[-1]}"


def _safe_error_message(exc: Exception, request: RunWebcolegiosImportRequest) -> str:
    message = str(exc)
    for sensitive_value in (request.contrasena, request.usuario):
        if sensitive_value:
            message = message.replace(sensitive_value, "***")
    return message


class RunWebcolegiosImport:
    def __init__(
        self,
        repository: WebcolegiosImportRepository,
        scraper: WebcolegiosScraperAdapter | None = None,
    ):
        self.repository = repository
        self.scraper = scraper or WebcolegiosScraperAdapter()

    def execute(self, request: RunWebcolegiosImportRequest) -> ImportSummary:
        return self._execute(request, include_students=True, include_teachers=True)

    def execute_students(self, request: RunWebcolegiosImportRequest) -> ImportSummary:
        return self._execute(request, include_students=True, include_teachers=False)

    def execute_teachers(self, request: RunWebcolegiosImportRequest) -> ImportSummary:
        return self._execute(request, include_students=False, include_teachers=True)

    def _execute(
        self,
        request: RunWebcolegiosImportRequest,
        *,
        include_students: bool,
        include_teachers: bool,
    ) -> ImportSummary:
        summary = ImportSummary()
        cleaner = CleanWebcolegiosTempTables(self.repository)

        logger.info(
            "Iniciando scraping WebColegios para usuario={}",
            _mask_user(request.usuario),
        )
        logger.info("Limpiando staging")
        cleaner.execute()
        try:
            scrape_result = self._scrape_by_mode(
                request,
                include_students=include_students,
                include_teachers=include_teachers,
            )
            summary.total_estudiantes_scrapeados = len(scrape_result.students)
            summary.total_docentes_scrapeados = len(scrape_result.teachers)
            logger.info(
                "Scraping retorno datos: estudiantes={}, docentes={}",
                summary.total_estudiantes_scrapeados,
                summary.total_docentes_scrapeados,
            )

            if include_students:
                logger.info("Guardando staging estudiantes")
                self.repository.save_staging_students(scrape_result.students)
            if include_teachers:
                logger.info("Guardando staging docentes")
                self.repository.save_staging_teachers(scrape_result.teachers)

            if include_students:
                logger.info("Validando estudiantes")
                SyncStudents(self.repository).execute(summary)
            if include_teachers:
                logger.info("Validando docentes")
                SyncTeachers(self.repository).execute(summary)
        except Exception as exc:
            safe_error = _safe_error_message(exc, request)
            logger.error("Error general en importacion WebColegios: {}", safe_error)
            summary.errores += 1
            self.repository.register_import_result(
                tipo_entidad=WEBCOLEGIOS_SYSTEM_ENTITY,
                documento_identidad="",
                datos="{}",
                estado="ERROR",
                observacion=f"Error general de importacion: {safe_error}",
            )
            summary.detalle.append(
                ImportDetail(
                    tipo="sistema",
                    documento=None,
                    nombre=None,
                    estado="ERROR",
                    observacion=f"Error general de importacion: {safe_error}",
                )
            )
        finally:
            logger.info("Limpiando staging")
            cleaner.execute()

        logger.info(
            "Importacion finalizada: estudiantes_insertados={}, estudiantes_actualizados={}, "
            "estudiantes_omitidos={}, estudiantes_pendientes={}, docentes_insertados={}, "
            "docentes_omitidos={}, errores={}",
            summary.estudiantes_insertados,
            summary.estudiantes_actualizados,
            summary.estudiantes_omitidos,
            summary.estudiantes_pendientes,
            summary.docentes_insertados,
            summary.docentes_omitidos,
            summary.errores,
        )
        return summary

    def _scrape_by_mode(
        self,
        request: RunWebcolegiosImportRequest,
        *,
        include_students: bool,
        include_teachers: bool,
    ):
        if include_students and include_teachers:
            return self.scraper.run(
                url=request.url,
                usuario=request.usuario,
                contrasena=request.contrasena,
            )
        if include_students:
            return self.scraper.run_students(
                url=request.url,
                usuario=request.usuario,
                contrasena=request.contrasena,
            )
        return self.scraper.run_teachers(
            url=request.url,
            usuario=request.usuario,
            contrasena=request.contrasena,
        )
