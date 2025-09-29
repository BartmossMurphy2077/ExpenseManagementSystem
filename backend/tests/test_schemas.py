import pytest
from datetime import datetime, date
from app.schemas import ExpenseCreate, Expense, Tag

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
    assert exp.dict()["title"] == "Groceries"

def test_invalid_expense_amount():
    with pytest.raises(ValueError):
        ExpenseCreate(title="Bad Expense", amount="not-a-float")
