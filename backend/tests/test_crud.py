from app import crud, schemas
from datetime import datetime

def test_create_and_get_expense(db, test_user):
    expense_data = schemas.ExpenseCreate(
        title="Coffee",
        amount=3.5,
        tags=["drink"],
        type="expense",
        timestamp=datetime(2025, 9, 20)
    )
    created = crud.create_expense(db, expense_data, test_user.id)
    assert created.id is not None
    assert created.title == "Coffee"
    assert len(created.tags) == 1
    assert created.tags[0].name == "drink"

    fetched = crud.get_expense(db, created.id, test_user.id)
    assert fetched.id == created.id
    assert fetched.title == "Coffee"

def test_update_expense(db, test_user):
    expense_data = schemas.ExpenseCreate(
        title="Book",
        amount=10,
        tags=["study"],
        type="expense",
        timestamp=datetime(2025, 9, 21)
    )
    expense = crud.create_expense(db, expense_data, test_user.id)

    updated_data = schemas.ExpenseCreate(
        title="Book Updated",
        amount=15,
        tags=["study", "fun"],
        type="expense",
        timestamp=datetime(2025, 9, 22)
    )
    updated = crud.update_expense(db, expense.id, updated_data, test_user.id)

    assert updated.title == "Book Updated"
    assert updated.amount == 15
    assert len(updated.tags) == 2
    assert sorted([t.name for t in updated.tags]) == ["fun", "study"]

def test_delete_expense(db, test_user):
    expense_data = schemas.ExpenseCreate(
        title="Snack",
        amount=5,
        tags=["food"],
        type="expense",
        timestamp=datetime(2025, 9, 23)
    )
    expense = crud.create_expense(db, expense_data, test_user.id)

    deleted = crud.delete_expense(db, expense.id, test_user.id)
    assert deleted is not None
    assert crud.get_expense(db, expense.id, test_user.id) is None

def test_get_expenses_in_range(db, test_user):
    expense1 = schemas.ExpenseCreate(
        title="Breakfast",
        amount=8.0,
        tags=["food"],
        type="expense",
        timestamp=datetime(2025, 9, 20)
    )
    expense2 = schemas.ExpenseCreate(
        title="Dinner",
        amount=20.0,
        tags=["food"],
        type="expense",
        timestamp=datetime(2025, 9, 25)
    )
    expense3 = schemas.ExpenseCreate(
        title="Snack",
        amount=5.0,
        tags=["food"],
        type="expense",
        timestamp=datetime(2025, 9, 28)
    )

    e1 = crud.create_expense(db, expense1, test_user.id)
    e2 = crud.create_expense(db, expense2, test_user.id)
    e3 = crud.create_expense(db, expense3, test_user.id)

    start_date = datetime(2025, 9, 21).date()
    end_date = datetime(2025, 9, 27).date()
    expenses_in_range = crud.get_expenses_in_range(db, start_date, end_date, test_user.id)

    assert len(expenses_in_range) == 1
    assert expenses_in_range[0].title == "Dinner"
