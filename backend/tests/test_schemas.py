from app import schemas
from datetime import datetime

def test_user_create_schema():
    u = schemas.UserCreate(username="test", email="a@b.com", password="pass")
    assert u.username == "test"
    assert u.email == "a@b.com"

def test_expense_schema():
    e = schemas.ExpenseCreate(title="T", amount=5.0)
    assert e.title == "T"
    assert e.amount == 5.0
