from app.core.security import get_password_hash

def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "¡Hola Mundo! El servidor backend SÍ funciona."}

def test_register_user(client):
    response = client.post(
        "/users/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_register_existing_email(client):
    # Primer registro
    client.post(
        "/users/register",
        json={"email": "test@example.com", "password": "password123"}
    )
    # Segundo registro con mismo email
    response = client.post(
        "/users/register",
        json={"email": "test@example.com", "password": "password456"}
    )
    assert response.status_code == 400

def test_login_user(client):
    # Registrar usuario
    client.post(
        "/users/register",
        json={"email": "login@example.com", "password": "mypassword"}
    )
    # Intentar login
    response = client.post(
        "/users/login",
        data={"username": "login@example.com", "password": "mypassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    client.post(
        "/users/register",
        json={"email": "wrong@example.com", "password": "mypassword"}
    )
    response = client.post(
        "/users/login",
        data={"username": "wrong@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
