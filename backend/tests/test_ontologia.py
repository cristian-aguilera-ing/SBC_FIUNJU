import pytest

def test_get_ontologia_materias(client, db_session):
    # Necesitamos un usuario autenticado para acceder a este endpoint
    client.post(
        "/users/register",
        json={"email": "user@ontologia.com", "password": "password"}
    )
    login_res = client.post(
        "/users/login",
        data={"username": "user@ontologia.com", "password": "password"}
    )
    token = login_res.json()["access_token"]

    # Llamar al endpoint protegido
    response = client.get(
        "/ontologia/materias",
        headers={"Authorization": f"Bearer {token}"}
    )

    # Nota: Esto fallará si la ontología no está cargada en app.state.knowledge_graph
    # En conftest/test setup idealmente cargaríamos una ontología mock o mínima.
    # Por ahora, verificamos que responda 200 OK (asumiendo que main.py carga la ontología real al inicio)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Si la ontología real se cargó, debería haber materias
    if len(data) > 0:
        assert "uri" in data[0]
        assert "label" in data[0]
