from app.core.db import SessionDep
from app.core.logger import setup_logger
from app.modules.webcolegios_import.domain.entities import ImportDetail, ImportSummary
from app.modules.webcolegios_import.domain.repositories import WEBCOLEGIOS_SYSTEM_ENTITY
from app.modules.webcolegios_import.domain.service import WebcolegiosImportService
from app.modules.webcolegios_import.infrastructure.repository import (
    WebcolegiosImportRepository,
)
from app.modules.webcolegios_import.infrastructure.scraper_adapter import (
    WebcolegiosScraperAdapter,
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


class RunWebcolegiosImportStudents:
    def __init__(self, session: SessionDep) -> None:
        repository = WebcolegiosImportRepository(session)
        self.service = WebcolegiosImportService(repository)
        self.repository = repository
        self.scraper = WebcolegiosScraperAdapter()

    def execute(self, request: RunWebcolegiosImportRequest) -> ImportSummary:
        summary = ImportSummary()
        logger.info(
            "Iniciando scraping estudiantes WebColegios para usuario={}",
            _mask_user(request.usuario),
        )
        logger.info("Limpiando staging")
        self.service.clear_staging()
        try:
            scrape_result = self.scraper.run_students(
                url=request.url,
                usuario=request.usuario,
                contrasena=request.contrasena,
            )
            summary.total_estudiantes_scrapeados = len(scrape_result.students)
            logger.info(
                "Scraping retorno datos: estudiantes={}",
                summary.total_estudiantes_scrapeados,
            )
            logger.info("Guardando staging estudiantes")
            self.repository.save_staging_students(scrape_result.students)
            logger.info("Validando estudiantes")
            self.service.sync_students(summary)
        except Exception as exc:
            safe_error = _safe_error_message(exc, request)
            logger.error(
                "Error general en importacion estudiantes WebColegios: {}", safe_error
            )
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
            self.service.clear_staging()

        logger.info(
            "Importacion estudiantes finalizada: insertados={}, actualizados={}, omitidos={}, pendientes={}, errores={}",
            summary.estudiantes_insertados,
            summary.estudiantes_actualizados,
            summary.estudiantes_omitidos,
            summary.estudiantes_pendientes,
            summary.errores,
        )
        return summary
