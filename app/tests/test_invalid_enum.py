def test_invalid_enum_returns_422(client):
    payload = {
        "estudiante_id": 1,
        "complementario_id": 1,
        "tipo_prueba": "matematicas",
        "estado": True,
        "periodo_id": 1,
    }
    response = client.post("/api/v1/tests/details", json=payload)
    assert response.status_code == 422
