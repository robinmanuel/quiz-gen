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


def test_refresh_token_rotation_and_logout(client):
    client.post(
        "/auth/register",
        json={"email": "bob@example.com", "username": "bob", "password": "password123"},
    )
    login = client.post(
        "/auth/token",
        data={"username": "bob", "password": "password123"},
    )
    assert login.status_code == 200
    tokens = login.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    # Refresh token rotation
    refreshed = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert refreshed.status_code == 200
    new_tokens = refreshed.json()
    assert new_tokens["access_token"] != access_token
    assert new_tokens["refresh_token"] != refresh_token

    # Reusing the old refresh token should fail (revoked)
    reuse = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert reuse.status_code == 401

    # Logout revokes current access token and refresh token
    logout_res = client.post(
        "/auth/logout",
        json={"refresh_token": new_tokens["refresh_token"]},
        headers={"Authorization": f"Bearer {new_tokens['access_token']}"},
    )
    assert logout_res.status_code == 204

    # Access token is now revoked
    me_after_logout = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {new_tokens['access_token']}"},
    )
    assert me_after_logout.status_code == 401


def test_update_and_delete_me(client):
    client.post(
        "/auth/register",
        json={"email": "profile@example.com", "username": "profileuser", "password": "password123"},
    )
    login = client.post(
        "/auth/token",
        data={"username": "profileuser", "password": "password123"},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Update email and password
    patch_res = client.patch(
        "/users/me",
        json={
            "email": "newprofile@example.com",
            "current_password": "password123",
            "new_password": "newpassword456",
        },
        headers=headers,
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["email"] == "newprofile@example.com"

    # Login with new password works
    relogin = client.post(
        "/auth/token",
        data={"username": "profileuser", "password": "newpassword456"},
    )
    assert relogin.status_code == 200

    # Delete account
    del_res = client.delete("/users/me", headers=headers)
    assert del_res.status_code == 204

    # Token no longer resolves a user
    after_del = client.get("/users/me", headers=headers)
    assert after_del.status_code == 401


def test_forgot_and_reset_password(client):
    client.post(
        "/auth/register",
        json={"email": "reset@example.com", "username": "resetuser", "password": "oldpassword123"},
    )

    forgot = client.post("/auth/forgot-password", json={"email": "reset@example.com"})
    assert forgot.status_code == 200
    reset_token = forgot.json()["reset_token"]
    assert reset_token is not None

    reset_res = client.post(
        "/auth/reset-password",
        json={"reset_token": reset_token, "new_password": "brandnewpassword123"},
    )
    assert reset_res.status_code == 200

    # Reusing the same reset token fails
    reuse_reset = client.post(
        "/auth/reset-password",
        json={"reset_token": reset_token, "new_password": "anotherpassword123"},
    )
    assert reuse_reset.status_code == 400

    # Login with the new password succeeds
    login_new = client.post(
        "/auth/token",
        data={"username": "resetuser", "password": "brandnewpassword123"},
    )
    assert login_new.status_code == 200

