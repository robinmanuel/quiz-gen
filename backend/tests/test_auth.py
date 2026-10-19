from app.schemas.user import UserCreate


def test_register_user(client):
    r = client.post(
        "/auth/register",
        json={"email": "bob@example.com", "username": "bob", "password": "password123"},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == "bob@example.com"
    assert data["username"] == "bob"
    assert "id" in data


def test_register_duplicate_email(client):
    # First registration
    client.post(
        "/auth/register",
        json={"email": "bob@example.com", "username": "bob", "password": "password123"},
    )
    # Duplicate email
    r = client.post(
        "/auth/register",
        json={"email": "bob@example.com", "username": "bob2", "password": "password123"},
    )
    assert r.status_code == 400
    assert "Email already registered" in r.json()["detail"]


def test_register_duplicate_username(client):
    client.post(
        "/auth/register",
        json={"email": "bob@example.com", "username": "bob", "password": "password123"},
    )
    r = client.post(
        "/auth/register",
        json={"email": "bob2@example.com", "username": "bob", "password": "password123"},
    )
    assert r.status_code == 400
    assert "Username already taken" in r.json()["detail"]


def test_login_success(client):
    client.post(
        "/auth/register",
        json={"email": "bob@example.com", "username": "bob", "password": "password123"},
    )
    r = client.post(
        "/auth/token",
        data={"username": "bob", "password": "password123"},
    )
    assert r.status_code == 200
    assert "access_token" in r.json()
    assert r.json()["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post(
        "/auth/register",
        json={"email": "bob@example.com", "username": "bob", "password": "password123"},
    )
    r = client.post(
        "/auth/token",
        data={"username": "bob", "password": "wrongpassword"},
    )
    assert r.status_code == 401


def test_get_me_success(client):
    client.post(
        "/auth/register",
        json={"email": "bob@example.com", "username": "bob", "password": "password123"},
    )
    login = client.post(
        "/auth/token",
        data={"username": "bob", "password": "password123"},
    )
    token = login.json()["access_token"]

    r = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["username"] == "bob"


def test_get_me_no_token(client):
    r = client.get("/users/me")
    assert r.status_code == 401
