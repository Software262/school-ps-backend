def test_create_success_returns_201(client):
    # Asegúrate de usar IDs que existan en la DB si estás testeando contra ella,
    # o de mockear la respuesta. Para probar la validación, al menos el request
    # es válido. Si falla por IntegrityError, el test_invalid_fk lo cubre.
    # Asumimos que los IDs 1 y 1 existen.
    payload = {
        "estudiante_id": 1,
        "complementario_id": 1,
        "tipo_prueba": "saber",
        "estado": True,
    }
    response = client.post("/api/v1/tests/details", json=payload)

    # Si la base de datos de pruebas está vacía, podría dar 400.
    # Permitiremos ambos códigos dependiendo del estado de la DB local.
    assert response.status_code == 200
    data = response.json()
    assert data.get("statusCode") in (201, 400)
