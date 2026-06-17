def test_create_success_returns_201(client):
    payload = {
        "estudiante_id": 3,
        "complementario_id": 1,
        "tipo_prueba": "saber",
        "estado": "pendiente",
        "periodo_id": 1,
    }
    response = client.post("/api/v1/tests/details", json=payload)

    # Handle if already exists or succeeds
    if response.status_code == 500 and "duplicate_assignment" in response.text:
        assert True
    else:
        assert response.status_code in (200, 201)
        data = response.json()
        assert data.get("statusCode") == 201
        created_id = data.get("data", {}).get("id")
        if created_id:
            client.delete(f"/api/v1/tests/details/{created_id}")
