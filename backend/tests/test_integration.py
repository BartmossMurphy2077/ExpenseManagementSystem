# backend/tests/test_integration.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.auth import get_current_user
from app import models, crud
from sqlalchemy.orm import Session


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    def override_get_current_user():
        # This will be set by individual tests when needed
        return getattr(client, '_test_user', None)

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def create_test_user_and_login(client, db):
    """Helper function to create user and return token"""
    # Test registration
    user_data = {
        "username": "integrationtest",
        "email": "integration@test.com",
        "password": "testpass123"
    }

    response = client.post("/register", json=user_data)
    assert response.status_code == 200
    user = response.json()
    assert user["username"] == "integrationtest"
    assert user["email"] == "integration@test.com"
    assert "id" in user

    # Test login
    login_data = {
        "username": "integrationtest",
        "password": "testpass123"
    }

    response = client.post("/login", json=login_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    return token_data["access_token"]


def test_user_registration_and_login(client, db):
    # Just test the registration and login process
    token = create_test_user_and_login(client, db)
    assert token is not None


def test_authenticated_endpoints(client, db):
    # First register and login
    token = create_test_user_and_login(client, db)
    headers = {"Authorization": f"Bearer {token}"}

    # Test /me endpoint
    response = client.get("/me", headers=headers)
    assert response.status_code == 200
    user = response.json()
    assert user["username"] == "integrationtest"

    # Test expense creation
    expense_data = {
        "title": "Integration Test Expense",
        "amount": 25.50,
        "tags": ["test", "integration"],
        "type": "expense"
    }

    response = client.post("/expenses", json=expense_data, headers=headers)
    assert response.status_code == 200
    expense = response.json()
    assert expense["title"] == "Integration Test Expense"
    assert expense["amount"] == 25.50
    assert len(expense["tags"]) == 2

    expense_id = expense["id"]

    # Test expense retrieval
    response = client.get("/expenses", headers=headers)
    assert response.status_code == 200
    expenses = response.json()
    assert len(expenses) == 1
    assert expenses[0]["id"] == expense_id

    # Test single expense retrieval
    response = client.get(f"/expenses/{expense_id}", headers=headers)
    assert response.status_code == 200
    retrieved_expense = response.json()
    assert retrieved_expense["id"] == expense_id

    # Test expense update
    update_data = {
        "title": "Updated Integration Test Expense",
        "amount": 30.00,
        "tags": ["test", "integration", "updated"],
        "type": "expense"
    }

    response = client.put(f"/expenses/{expense_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    updated_expense = response.json()
    assert updated_expense["title"] == "Updated Integration Test Expense"
    assert updated_expense["amount"] == 30.00
    assert len(updated_expense["tags"]) == 3

    # Test expense deletion
    response = client.delete(f"/expenses/{expense_id}", headers=headers)
    assert response.status_code == 200

    # Verify expense is deleted
    response = client.get("/expenses", headers=headers)
    assert response.status_code == 200
    expenses = response.json()
    assert len(expenses) == 0


def test_unauthorized_access(client, db):
    # Test accessing protected endpoints without token
    response = client.get("/me")
    assert response.status_code == 403

    response = client.get("/expenses")
    assert response.status_code == 403

    response = client.post("/expenses", json={"title": "test", "amount": 10})
    assert response.status_code == 403


def test_invalid_token(client, db):
    headers = {"Authorization": "Bearer invalid_token"}

    response = client.get("/me", headers=headers)
    assert response.status_code == 401

    response = client.get("/expenses", headers=headers)
    assert response.status_code == 401


def test_duplicate_registration(client, db):
    # Register first user
    user_data = {
        "username": "duplicate_test",
        "email": "duplicate@test.com",
        "password": "testpass123"
    }

    response = client.post("/register", json=user_data)
    assert response.status_code == 200

    # Try to register with same username
    duplicate_username = {
        "username": "duplicate_test",
        "email": "different@test.com",
        "password": "testpass123"
    }

    response = client.post("/register", json=duplicate_username)
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]

    # Try to register with same email
    duplicate_email = {
        "username": "different_user",
        "email": "duplicate@test.com",
        "password": "testpass123"
    }

    response = client.post("/register", json=duplicate_email)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


def test_invalid_login(client, db):
    # Register a user first
    user_data = {
        "username": "logintest",
        "email": "login@test.com",
        "password": "testpass123"
    }

    response = client.post("/register", json=user_data)
    assert response.status_code == 200

    # Test wrong password
    wrong_password = {
        "username": "logintest",
        "password": "wrongpassword"
    }

    response = client.post("/login", json=wrong_password)
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

    # Test wrong username
    wrong_username = {
        "username": "wronguser",
        "password": "testpass123"
    }

    response = client.post("/login", json=wrong_username)
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]
