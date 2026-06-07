"""
Módulo de pruebas expandido y refactorizado para Cafetería.
Author: Danilo Castillejo
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import status
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.db import get_session
from app.modules.cafeteria.domain.service import CafeteriaService
from app.modules.cafeteria.infrastructure.models import Cafeteria
from app.modules.enrollment.domain.entities import StudentGeneralInfo

# --- CONFIGURACIÓN DE MOCKS ---
mock_db_session = MagicMock()


def override_get_session():
    yield mock_db_session


app.dependency_overrides[get_session] = override_get_session


# --- TESTS ---


@pytest.mark.asyncio
async def test_get_status_list_logic():
    mock_repo = MagicMock()
    mock_enrollment = MagicMock()
    service = CafeteriaService(repository=mock_repo, student_service=mock_enrollment)

    fake_debtor = Cafeteria(id=1, estudiante_id=10, estado_cafeteria=False)
    mock_repo.get_all_debtors = AsyncMock(return_value=[fake_debtor])

    fake_student_info = StudentGeneralInfo(
        id=10, nombre="Sara", documento="2000", grado_nombre="Décimo"
    )
    mock_enrollment.get_students_bulk = MagicMock(return_value=[fake_student_info])

    results = await service.get_status_list(periodo_id=1)
    assert len(results) == 1
    assert results[0].nombre == "Sara"


@pytest.mark.asyncio
async def test_api_list_endpoint_success():
    # Mockeamos el execute del caso de uso directamente para el test de API
    with patch(
        "app.modules.cafeteria.application.get_status.GetStatus.execute",
        new_callable=AsyncMock,
    ) as mock_exec:
        mock_exec.return_value = []
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/api/v1/cafeteria/list/1")

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_api_grades_endpoint_success():
    with patch(
        "app.modules.cafeteria.application.get_grades.GetGrades.execute",
        new_callable=AsyncMock,
    ) as mock_exec:
        mock_exec.return_value = []
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/api/v1/cafeteria/grades")

        assert response.status_code == status.HTTP_200_OK
