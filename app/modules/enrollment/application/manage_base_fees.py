from app.core.db import SessionDep
from app.modules.enrollment.infrastructure.repository import SQLEnrollmentRepository
from app.modules.enrollment.schemas.request import (
    CopyBaseFeesRequest,
    SingleGradeFeeRequest,
    UpsertBaseFeesRequest,
)
from app.modules.enrollment.schemas.response import (
    BaseFeeGradeResponse,
    BaseFeesListResponse,
)


class GetBaseFees:
    """Caso de uso: obtener tarifas base de matrícula y pensión por año."""

    def __init__(self, session: SessionDep) -> None:
        self.repo = SQLEnrollmentRepository(session)

    def execute(self, year: int) -> BaseFeesListResponse:
        fees = self.repo.get_base_fees(year)
        total_config = sum(1 for f in fees if f["configurado"])
        return BaseFeesListResponse(
            anio=year,
            total_grados=len(fees),
            total_configurados=total_config,
            tarifas=[BaseFeeGradeResponse(**f) for f in fees],
        )


class UpsertBaseFees:
    """Caso de uso: guardar o actualizar tarifas base por lote."""

    def __init__(self, session: SessionDep) -> None:
        self.repo = SQLEnrollmentRepository(session)

    def execute(self, request: UpsertBaseFeesRequest) -> BaseFeesListResponse:
        tarifas_dict = [t.model_dump() for t in request.tarifas]
        self.repo.upsert_base_fees(request.anio, tarifas_dict)
        fees = self.repo.get_base_fees(request.anio)
        total_config = sum(1 for f in fees if f["configurado"])
        return BaseFeesListResponse(
            anio=request.anio,
            total_grados=len(fees),
            total_configurados=total_config,
            tarifas=[BaseFeeGradeResponse(**f) for f in fees],
        )


class CopyBaseFees:
    """Caso de uso: copiar tarifas de un año a otro."""

    def __init__(self, session: SessionDep) -> None:
        self.repo = SQLEnrollmentRepository(session)

    def execute(self, request: CopyBaseFeesRequest) -> BaseFeesListResponse:
        self.repo.copy_base_fees(
            request.anio_origen,
            request.anio_destino,
            request.incremento_porcentaje,
        )
        fees = self.repo.get_base_fees(request.anio_destino)
        total_config = sum(1 for f in fees if f["configurado"])
        return BaseFeesListResponse(
            anio=request.anio_destino,
            total_grados=len(fees),
            total_configurados=total_config,
            tarifas=[BaseFeeGradeResponse(**f) for f in fees],
        )


class InitializeDefaultBaseFees:
    """Caso de uso: inicializar tarifas sugeridas por defecto para un año."""

    def __init__(self, session: SessionDep) -> None:
        self.repo = SQLEnrollmentRepository(session)

    def execute(self, year: int) -> BaseFeesListResponse:
        self.repo.initialize_default_base_fees(year)
        fees = self.repo.get_base_fees(year)
        total_config = sum(1 for f in fees if f["configurado"])
        return BaseFeesListResponse(
            anio=year,
            total_grados=len(fees),
            total_configurados=total_config,
            tarifas=[BaseFeeGradeResponse(**f) for f in fees],
        )


class UpdateSingleGradeFee:
    """Caso de uso: actualizar o fijar tarifa base para un grado individual."""

    def __init__(self, session: SessionDep) -> None:
        self.repo = SQLEnrollmentRepository(session)

    def execute(
        self, grado_id: int, request: SingleGradeFeeRequest
    ) -> BaseFeeGradeResponse:
        self.repo.upsert_base_fees(
            request.anio,
            [
                {
                    "grado_id": grado_id,
                    "matricula_valor": request.matricula_valor,
                    "pension_valor": request.pension_valor,
                }
            ],
        )
        fees = self.repo.get_base_fees(request.anio)
        match = next((f for f in fees if f["grado_id"] == grado_id), None)
        if not match:
            raise ValueError(f"Grado {grado_id} no encontrado")
        return BaseFeeGradeResponse(**match)
