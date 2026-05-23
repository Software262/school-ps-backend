import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.core.db import get_session
from app.main import app
from app.modules.enrollment.infrastructure.models import Acudiente, Complementario, Estudiante, Grado
from app.modules.training_schools.infrastructure.models import DetalleEscuelaFormacion

TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

SQLModel.metadata.create_all(engine)


def get_test_session():
    with Session(engine) as session:
        yield session


app.dependency_overrides[get_session] = get_test_session


@pytest.fixture(scope="session")
def test_data():
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        grado = Grado(nombre="Primero")
        acudiente = Acudiente(
            nombre="Padre Prueba",
            parentesco="Padre",
            telefono="3001234567",
            correo="padre@example.com",
        )
        session.add(grado)
        session.add(acudiente)
        session.commit()
        session.refresh(grado)
        session.refresh(acudiente)

        estudiante = Estudiante(
            nombre="Estudiante Prueba",
            documento="123456789",
            activo=True,
            grado_id=grado.id,
            acudiente_id=acudiente.id,
        )
        complementario = Complementario(
            tipo_complementario="Artes",
            anio=2026,
            valor=100,
            estado_complemento="activo",
            uso_matricula=False,
        )
        session.add(estudiante)
        session.add(complementario)
        session.commit()
        session.refresh(estudiante)
        session.refresh(complementario)

        return {
            "student_id": estudiante.id,
            "complementario_id": complementario.id,
        }


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_enroll_student_endpoint_success(client: TestClient, test_data: dict):
    payload = {
        "estudiante_id": test_data["student_id"],
        "complementario_id": test_data["complementario_id"],
        "mes": "Mayo",
    }
    response = client.post("/api/v1/training-schools/enroll", json=payload)

    assert response.status_code == 201
    result = response.json()
    assert result["data"]["estudiante_id"] == test_data["student_id"]
    assert result["data"]["complementario_id"] == test_data["complementario_id"]
    assert result["data"]["mes"] == "Mayo"
    assert result["data"]["activo"] is True
    assert result["data"]["estado_escuela"] is False
    assert result["data"]["motivo_baja"] is None


def test_register_payment_endpoint_success(client: TestClient, test_data: dict):
    payload = {
        "estudiante_id": test_data["student_id"],
        "complementario_id": test_data["complementario_id"],
        "mes": "Mayo",
    }
    response = client.post("/api/v1/training-schools/payments", json=payload)

    assert response.status_code == 200
    result = response.json()
    assert result["data"]["estado_escuela"] is True
    assert result["data"]["activo"] is True


def test_get_student_status_endpoint_success(client: TestClient, test_data: dict):
    response = client.get(f"/api/v1/training-schools/students/{test_data['student_id']}/status")

    assert response.status_code == 200
    result = response.json()
    assert result["data"]["estudiante_id"] == test_data["student_id"]
    assert result["data"]["paz_y_salvo"] is True
    assert "Paz y salvo" in result["data"]["detalle"]


def test_unsubscribe_student_endpoint_success(client: TestClient, test_data: dict):
    payload = {"motivo": "No puede asistir"}
    response = client.patch(
        f"/api/v1/training-schools/enrollments/{test_data['student_id']}/{test_data['complementario_id']}/Mayo/unsubscribe",
        json=payload,
    )

    assert response.status_code == 200
    result = response.json()
    assert result["data"]["activo"] is False
    assert result["data"]["motivo_baja"] == "No puede asistir"


def test_list_student_enrollments_endpoint(client: TestClient, test_data: dict):
    response = client.get(f"/api/v1/training-schools/students/{test_data['student_id']}/enrollments")

    assert response.status_code == 200
    result = response.json()
    assert isinstance(result["data"], list)
    assert len(result["data"]) >= 1
    assert any(enrollment["mes"] == "Mayo" for enrollment in result["data"])
