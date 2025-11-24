import pytest
from datetime import datetime
from app import schemas

def test_register_login_expense_flow(client, test_user):
    # Register
    r = client.post("/register", json=test_user)
    assert r.status_code == 200
    # Login
    r = client.post("/login", json={"username": test_user["username"], "password": test_user["password"]})
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    # Add expense
    expense_data = {"title": "Lunch", "amount": 10.0, "tags": ["food"]}
    r = client.post("/expenses", json=expense_data, headers=headers)
    assert r.status_code == 200
    exp = r.json()
    assert exp["title"] == "Lunch"
    # List expenses
    r = client.get("/expenses", headers=headers)
    assert r.status_code == 200
    assert len(r.json()) == 1
