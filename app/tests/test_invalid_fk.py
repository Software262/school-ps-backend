def test_invalid_fk_returns_400(client):
    payload = {
        "estudiante_id": 999999,  # ID que no existe
        "complementario_id": 1,
        "tipo_prueba": "saber",
        "estado": "pendiente",
        "periodo_id": 1,
    }
    response = client.post("/api/v1/tests/details", json=payload)
    assert response.status_code in [200, 400, 422]
    if response.status_code == 200:
        data = response.json()
        assert data.get("statusCode") == 400
        assert (
            "IntegrityError" in response.text
            or "FOREIGN KEY" in response.text
            or "message" in data
        )
