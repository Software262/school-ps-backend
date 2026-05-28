import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client():
    """Cliente HTTP reutilizable para todos los tests."""
    with TestClient(app) as c:
        yield c
