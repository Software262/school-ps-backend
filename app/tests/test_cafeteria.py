"""
Módulo de pruebas expandido y refactorizado para Cafetería.
Cubre la nueva arquitectura de servicios desacoplados.
Author: Danilo Castillejo
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import status
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.db import get_session
from app.modules.cafeteria.api.routes import get_student_service
from app.modules.cafeteria.domain.service import CafeteriaService
from app.modules.cafeteria.infrastructure.models import Cafeteria
from app.modules.cafeteria.domain.entities import DebtorEntity
from app.modules.enrollment.domain.entities import StudentGeneralInfo

# --- CONFIGURACIÓN DE MOCKS PARA API ---

mock_db_session = MagicMock()
mock_ext_student_service = MagicMock()


def override_get_session():
    yield mock_db_session


def override_get_student_service():
    return mock_ext_student_service


# Aplicamos los overrides para que los tests de API no toquen la DB real
app.dependency_overrides[get_session] = override_get_session
app.dependency_overrides[get_student_service] = override_get_student_service


# --- 1. TESTS DE LÓGICA DE NEGOCIO (UNIT TESTS) ---


@pytest.mark.asyncio
async def test_get_status_list_cross_module_logic():
    """
    Verifica que el servicio de cafetería combine correctamente
    sus datos locales con los datos del servicio externo de Enrollment.
    """
    mock_repo = MagicMock()
    mock_enrollment = MagicMock()
    service = CafeteriaService(repository=mock_repo, student_service=mock_enrollment)

    fake_debtor = Cafeteria(
        id=1, estudiante_id=10, estado_cafeteria=False, observaciones="Debe"
    )
    mock_repo.get_all_debtors = AsyncMock(return_value=[fake_debtor])

    # CORRECCIÓN: Se eliminó 'activo' que no existe en StudentGeneralInfo
    fake_student_info = StudentGeneralInfo(
        id=10, nombre="Sara Rodriguez", documento="2000", grado_nombre="Décimo"
    )
    mock_enrollment.get_students_bulk = MagicMock(return_value=[fake_student_info])

    results = await service.get_status_list(periodo_id=1)

    assert len(results) == 1
    assert isinstance(results[0], DebtorEntity)
    assert results[0].nombre == "Sara Rodriguez"
    assert results[0].grado == "Décimo"
    assert results[0].observaciones == "Debe"


@pytest.mark.asyncio
async def test_export_report_csv_has_bom():
    from app.modules.cafeteria.application.export_report import ExportReport
    from unittest.mock import patch  # Añadir este import

    mock_enrollment = MagicMock()
    use_case = ExportReport(session=mock_db_session, student_service=mock_enrollment)
    mock_row = ["2000", "Sara Rodríguez", "Décimo", "DEUDA", "Obs"]

    # Fix: Usar patch en lugar de asignación directa
    with patch.object(use_case.service, "format_report_data", return_value=[mock_row]):
        csv_content = await use_case.execute(periodo_id=1)
        assert csv_content.startswith("\ufeff")


@pytest.mark.asyncio
async def test_search_normalization_logic():
    """Verifica que la búsqueda envíe el texto normalizado (minúsculas)."""
    mock_repo = MagicMock()
    mock_enrollment = MagicMock()
    service = CafeteriaService(repository=mock_repo, student_service=mock_enrollment)

    mock_enrollment.search_active_students = MagicMock(return_value=[])

    await service.search_general_students_flat(query="JUAN PEREZ", grado_id=None)

    # El servicio debe normalizar a minúsculas antes de llamar a Enrollment
    mock_enrollment.search_active_students.assert_called_once_with(
        query="juan perez", grado_id=None, limit=15
    )


# --- 2. TESTS DE INTEGRACIÓN DE API (ENDPOINT TESTS) ---


@pytest.mark.asyncio
async def test_api_list_endpoint_success():
    """Verifica que el router esté bien configurado con la nueva inyección."""
    # Configurar los mocks para que devuelvan listas vacías
    mock_db_session.execute.return_value.all.return_value = []
    mock_ext_student_service.get_students_bulk.return_value = []

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/cafeteria/list/1")

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_api_grades_cross_module():
    """Verifica que el endpoint de grados llame al servicio de enrollment."""
    mock_ext_student_service.get_all_grades.return_value = []

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/cafeteria/grades")

    assert response.status_code == status.HTTP_200_OK
    mock_ext_student_service.get_all_grades.assert_called_once()
