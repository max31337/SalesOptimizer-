from fastapi.testclient import TestClient
import pytest

def test_login_success(client, test_admin):
    response = client.post("/api/auth/login/", json={
        "email": "admin@test.com",
        "password": "admin123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["role"] == "admin"

def test_login_invalid_credentials(client):
    response = client.post("/api/auth/login/", json={
        "email": "wrong@test.com",
        "password": "wrong123"
    })
    assert response.status_code == 401

def test_check_session(client, test_admin):
    # First login to get token
    login_response = client.post("/api/auth/login/", json={
        "email": "admin@test.com",
        "password": "admin123"
    })
    token = login_response.json()["access_token"]
    
    # Check session with token
    response = client.get("/api/auth/check-session", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert response.json()["role"] == "admin"