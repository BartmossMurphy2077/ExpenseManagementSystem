import pytest
from app import crud, auth
from fastapi import status

def test_password_hashing_and_verification():
    password = "mysecret"
    hashed = auth.get_password_hash(password)
    assert auth.verify_password(password, hashed)
    assert not auth.verify_password("wrongpassword", hashed)

def test_register_and_login(client, test_user):
    # Register
    response = client.post("/register", json=test_user)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user["username"]

    # Login
    response = client.post("/login", json={"username": test_user["username"], "password": test_user["password"]})
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data

def test_register_duplicate_user(client, test_user):
    client.post("/register", json=test_user)
    response = client.post("/register", json=test_user)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]
