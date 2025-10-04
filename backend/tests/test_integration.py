# backend/tests/test_integration.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.auth import AuthService
from datetime import timedelta


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_user_registration_and_login(client):
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


def test_authenticated_endpoints(client):
    # First register and login
    token = test_user_registration_and_login(client)
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


def test_unauthorized_access(client):
    # Test accessing protected endpoints without token
    response = client.get("/me")
    assert response.status_code == 401

    response = client.get("/expenses")
    assert response.status_code == 401

    response = client.post("/expenses", json={"title": "test", "amount": 10})
    assert response.status_code == 401


def test_invalid_token(client):
    headers = {"Authorization": "Bearer invalid_token"}

    response = client.get("/me", headers=headers)
    assert response.status_code == 401

    response = client.get("/expenses", headers=headers)
    assert response.status_code == 401
