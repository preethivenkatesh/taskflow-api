"""Tests for user endpoints."""


def test_register_user(client):
    resp = client.post(
        "/api/v1/users/",
        json={"username": "bob", "email": "bob@test.com", "password": "strongpass1"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "bob"
    assert data["email"] == "bob@test.com"
    assert "id" in data


def test_register_duplicate_username(client, sample_user):
    resp = client.post(
        "/api/v1/users/",
        json={"username": "alice", "email": "new@test.com", "password": "strongpass1"},
    )
    assert resp.status_code == 409


def test_get_user(client, sample_user):
    uid = sample_user["id"]
    resp = client.get(f"/api/v1/users/{uid}")
    assert resp.status_code == 200
    assert resp.json()["username"] == "alice"


def test_get_user_not_found(client):
    resp = client.get("/api/v1/users/9999")
    assert resp.status_code == 404
