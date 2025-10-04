# backend/tests/test_schemas.py
import pytest
from datetime import datetime, date
from app.schemas import ExpenseCreate, Expense, Tag, UserCreate, UserUpdate
from pydantic import ValidationError


def test_expense_create_schema():
    data = {
        "title": "Dinner",
        "amount": 20.0,
        "tags": ["food", "friends"],
        "type": "expense",
        "timestamp": datetime.today()
    }
    expense = ExpenseCreate(**data)
    assert expense.title == "Dinner"
    assert expense.amount == 20.0
    assert "food" in expense.tags


def test_expense_response_schema():
    tag = Tag(id="123", name="food")
    exp = Expense(
        id="abc",
        title="Groceries",
        amount=50,
        timestamp=datetime.today(),
        tags=[tag]
    )
    assert exp.tags[0].name == "food"
    assert exp.model_dump()["title"] == "Groceries"


def test_invalid_expense_amount():
    with pytest.raises(ValidationError):
        ExpenseCreate(title="Bad Expense", amount="not-a-float")


def test_user_create_schema():
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }
    user = UserCreate(**user_data)
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.password == "testpass123"


def test_user_update_schema():
    # Test partial update
    update_data = UserUpdate(username="newusername")
    assert update_data.username == "newusername"
    assert update_data.email is None
    assert update_data.password is None

    # Test full update
    full_update = UserUpdate(
        username="newusername",
        email="new@example.com",
        password="newpass123"
    )
    assert full_update.username == "newusername"
    assert full_update.email == "new@example.com"
    assert full_update.password == "newpass123"


def test_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(username="test", email="invalid-email", password="pass")
