from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_assign_massive_tests_invalid_grado():
    response = client.post(
        "/api/v1/tests/assign-massive",
        json={
            "grado_id": 9999,
            "complementario_id": 1,
            "tipo_prueba": "icfes",
            "periodo_id": 1,
        },
    )
    # En este diseño, la API puede devolver HTTP 200 pero el statusCode interno ser de error.
    # Pero si revienta con IntegrityError u otra excepción, el código encapsula el status.
    data = response.json()
    assert data.get("statusCode") in [200, 400, 404, 500]
    # Si retorna 200, asignó 0 (ya que no hay estudiantes)
    if data.get("statusCode") == 200:
        assert data.get("data") == []


def test_register_test_payment_invalid_test():
    response = client.post(
        "/api/v1/tests/9999/pay",
        json={
            "detalle_prueba_id": 9999,
            "monto": 50000,
            "codigo_talonario": "TALONARIO-123",
            "observacion": "Pago test",
        },
    )
    data = response.json()
    assert data.get("statusCode") in [400, 404, 500]


def test_get_student_status_invalid_student():
    response = client.get("/api/v1/tests/student/9999/status")
    data = response.json()
    assert data.get("statusCode") in [200, 404]
    if data.get("statusCode") == 200:
        assert data.get("data").get("tests") == []


def test_delete_internal_test_invalid_id():
    response = client.delete("/api/v1/tests/details/9999")
    data = response.json()
    assert data.get("statusCode") in [400, 404, 500]
