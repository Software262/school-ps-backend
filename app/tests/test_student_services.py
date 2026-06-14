import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.core.db import get_session
from app.main import app
from app.modules.enrollment.domain.service import StudentService
from app.modules.enrollment.infrastructure.models import (
    Acudiente,
    Complementario,
    Estudiante,
    Grado,
    TipoComplementario,
)
from app.modules.enrollment.infrastructure.repository import SQLEnrollmentRepository
from app.modules.enrollment.schemas.response import StudentResponse

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(test_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine, expire_on_commit=False) as session:
        yield session
    SQLModel.metadata.drop_all(test_engine)


def test_student_service_all_functionalities(session):
    # 1. Seed base data: Grados
    grado_10 = Grado(nombre="Décimo")
    grado_11 = Grado(nombre="Once")
    session.add(grado_10)
    session.add(grado_11)
    session.commit()
    session.refresh(grado_10)
    session.refresh(grado_11)

    # Seed base data: Acudiente
    acudiente = Acudiente(
        nombre="Carlos Gomez",
        parentesco="Padre",
        telefono="3112223344",
        correo="carlos@gmail.com",
    )
    session.add(acudiente)
    session.commit()
    session.refresh(acudiente)

    assert acudiente.id is not None
    assert grado_10.id is not None
    assert grado_11.id is not None

    # Seed base data: Estudiantes
    est1 = Estudiante(
        nombre="Juan Andres Cepeda",
        documento="1005777888",
        grado_id=grado_10.id,
        acudiente_id=acudiente.id,
        activo=True,
    )
    est2 = Estudiante(
        nombre="Maria Camila Cepeda",
        documento="1005111222",
        grado_id=grado_10.id,
        acudiente_id=acudiente.id,
        activo=True,
    )
    est3 = Estudiante(
        nombre="Felipe Martinez",
        documento="1005999000",
        grado_id=grado_11.id,
        acudiente_id=acudiente.id,
        activo=True,
    )
    est_inactivo = Estudiante(
        nombre="Luis Perez",
        documento="1005555666",
        grado_id=grado_11.id,
        acudiente_id=acudiente.id,
        activo=False,  # Inactive
    )
    session.add(est1)
    session.add(est2)
    session.add(est3)
    session.add(est_inactivo)
    session.commit()
    session.refresh(est1)
    session.refresh(est2)
    session.refresh(est3)
    session.refresh(est_inactivo)

    # Instanciar repositorio y servicio
    repo = SQLEnrollmentRepository(session)
    student_service = StudentService(repo)

    # Test 1: Búsqueda general de estudiantes activos (search_active_students)
    # Sin filtros
    all_active = student_service.search_active_students(limit=10, offset=0)
    assert len(all_active) == 3
    active_ids = {s.id for s in all_active}
    assert est_inactivo.id not in active_ids

    # Búsqueda por query (nombre parcial, normalizado a minúsculas)
    res_query = student_service.search_active_students(query="cepeda")
    assert len(res_query) == 2
    assert {s.nombre for s in res_query} == {
        "Juan Andres Cepeda",
        "Maria Camila Cepeda",
    }

    # Búsqueda por query (documento exacto o parcial)
    res_doc = student_service.search_active_students(query="1005111222")
    assert len(res_doc) == 1
    assert res_doc[0].nombre == "Maria Camila Cepeda"

    # Filtro por grado
    res_grade = student_service.search_active_students(grado_id=grado_11.id)
    assert len(res_grade) == 1
    assert res_grade[0].nombre == "Felipe Martinez"

    # Paginación (limit / offset)
    res_page1 = student_service.search_active_students(limit=2, offset=0)
    assert len(res_page1) == 2
    res_page2 = student_service.search_active_students(limit=2, offset=2)
    assert len(res_page2) == 1

    # Test 2: Servicio de Información por Lote (get_students_bulk)
    bulk_res = student_service.get_students_bulk([est1.id or 1, est3.id or 3])
    assert len(bulk_res) == 2
    assert {s.nombre for s in bulk_res} == {"Juan Andres Cepeda", "Felipe Martinez"}
    assert {s.grado_nombre for s in bulk_res} == {"Décimo", "Once"}

    # Caso lista vacía
    assert student_service.get_students_bulk([]) == []

    # Test 3: Servicio de Listado de Grados (get_all_grades)
    all_grades = student_service.get_all_grades()
    assert len(all_grades) == 2
    assert {g.nombre for g in all_grades} == {"Décimo", "Once"}

    # Test 4: get_student_by_id (Obtener entidad Estudiante cruda por ID)
    raw_est = student_service.get_student_by_id(est1.id or 1)
    assert raw_est is not None
    assert raw_est.nombre == "Juan Andres Cepeda"
    assert raw_est.documento == "1005777888"
    assert raw_est.activo is True

    # No existente
    assert student_service.get_student_by_id(99999) is None

    # Test 5: get_students_by_grade (Obtener lista de entidades Estudiante crudas por grado)
    grade_10_students = student_service.get_students_by_grade(grado_10.id)
    assert len(grade_10_students) == 2
    assert {s.nombre for s in grade_10_students} == {
        "Juan Andres Cepeda",
        "Maria Camila Cepeda",
    }
    # Verifica que son objetos StudentResponse y tienen sus campos/atributos completos
    assert isinstance(grade_10_students[0], StudentResponse)


@pytest.fixture(name="client")
def client_fixture(session):
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_student_endpoints(session, client):
    # 1. Seed base data: Grados
    grado_10 = Grado(nombre="Décimo")
    grado_11 = Grado(nombre="Once")
    session.add(grado_10)
    session.add(grado_11)
    session.commit()
    session.refresh(grado_10)
    session.refresh(grado_11)

    # Seed base data: Acudiente
    acudiente = Acudiente(
        nombre="Carlos Gomez",
        parentesco="Padre",
        telefono="3112223344",
        correo="carlos@gmail.com",
    )
    session.add(acudiente)
    session.commit()
    session.refresh(acudiente)

    assert acudiente.id is not None
    assert grado_10.id is not None
    assert grado_11.id is not None

    # Seed base data: Estudiantes
    est1 = Estudiante(
        nombre="Juan Andres Cepeda",
        documento="1005777888",
        grado_id=grado_10.id,
        acudiente_id=acudiente.id,
        activo=True,
    )
    est2 = Estudiante(
        nombre="Maria Camila Cepeda",
        documento="1005111222",
        grado_id=grado_10.id,
        acudiente_id=acudiente.id,
        activo=True,
    )
    est_inactivo = Estudiante(
        nombre="Luis Perez",
        documento="1005555666",
        grado_id=grado_11.id,
        acudiente_id=acudiente.id,
        activo=False,  # Inactive
    )
    session.add(est1)
    session.add(est2)
    session.add(est_inactivo)
    session.commit()
    session.refresh(est1)
    session.refresh(est2)
    session.refresh(est_inactivo)

    # Endpoint 1: GET /api/v1/enrollment/students/active (Search active students)
    resp = client.get("/api/v1/enrollment/students/active", params={"query": "Cepeda"})
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert len(data) == 2
    assert {s["nombre"] for s in data} == {"Juan Andres Cepeda", "Maria Camila Cepeda"}
    assert "grado_nombre" in data[0]

    # Filter by grade
    resp_grade = client.get(
        "/api/v1/enrollment/students/active", params={"grado_id": grado_11.id}
    )
    assert resp_grade.status_code == status.HTTP_200_OK
    assert len(resp_grade.json()) == 0  # Since est_inactivo is False (inactive)

    # Endpoint 2: POST /api/v1/enrollment/students/bulk (Retrieve student basic info in bulk)
    resp_bulk = client.post(
        "/api/v1/enrollment/students/bulk", json=[est1.id, est_inactivo.id]
    )
    assert resp_bulk.status_code == status.HTTP_200_OK
    data_bulk = resp_bulk.json()
    assert len(data_bulk) == 2
    assert {s["nombre"] for s in data_bulk} == {"Juan Andres Cepeda", "Luis Perez"}

    # Endpoint 3: GET /api/v1/enrollment/grades (List all grades)
    resp_grades = client.get("/api/v1/enrollment/grades")
    assert resp_grades.status_code == status.HTTP_200_OK
    data_grades = resp_grades.json()
    assert len(data_grades) == 2
    assert {g["nombre"] for g in data_grades} == {"Décimo", "Once"}


def test_get_complementary_concepts_endpoint(session, client):
    # Seed complementary concepts
    tipo = TipoComplementario(nombre="General", estado=True)
    session.add(tipo)
    session.flush()

    assert tipo.id is not None

    c1 = Complementario(
        nombre="Seguro Estudiantil",
        tipo_complementario_id=tipo.id,
        anio=2026,
        valor=50000,
        estado_complemento="Activo",
    )
    c2 = Complementario(
        nombre="Sistematización",
        tipo_complementario_id=tipo.id,
        anio=2026,
        valor=30000,
        estado_complemento="Activo",
    )
    c3 = Complementario(
        nombre="Pensión Especial",
        tipo_complementario_id=tipo.id,
        anio=2026,
        valor=100000,
        estado_complemento="Inactivo",  # Inactive
    )
    c4 = Complementario(
        nombre="Derechos de Grado",
        tipo_complementario_id=tipo.id,
        anio=2025,  # Different year
        valor=80000,
        estado_complemento="Activo",
    )
    session.add_all([c1, c2, c3, c4])
    session.commit()

    # Call the endpoint
    resp = client.get("/api/v1/enrollment/complementary", params={"year": 2026})
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()

    # Check that we only get Active concepts for the year 2026
    assert len(data) == 2
    assert {c["tipo_complementario"] for c in data} == {
        "Seguro Estudiantil",
        "Sistematización",
    }
    assert {c["valor"] for c in data} == {50000, 30000}
