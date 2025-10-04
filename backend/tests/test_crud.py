# backend/tests/test_crud.py
from app import crud, schemas
from datetime import datetime, date


def test_create_and_get_expense(db, test_user):
    expense_data = schemas.ExpenseCreate(
        title="Coffee",
        amount=3.5,
        tags=["drink"],
        type="expense",
        timestamp=datetime(2025, 9, 20)
    )
    created = crud.ExpenseCRUD.create_expense(db, expense_data, test_user.id)
    assert created.id is not None
    assert created.title == "Coffee"
    assert len(created.tags) == 1
    assert created.tags[0].name == "drink"

    fetched = crud.ExpenseCRUD.get_expense(db, created.id, test_user.id)
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
    expense = crud.ExpenseCRUD.create_expense(db, expense_data, test_user.id)

    updated_data = schemas.ExpenseCreate(
        title="Book Updated",
        amount=15,
        tags=["study", "fun"],
        type="expense",
        timestamp=datetime(2025, 9, 22)
    )
    updated = crud.ExpenseCRUD.update_expense(db, expense.id, updated_data, test_user.id)

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
    expense = crud.ExpenseCRUD.create_expense(db, expense_data, test_user.id)

    deleted = crud.ExpenseCRUD.delete_expense(db, expense.id, test_user.id)
    assert deleted is not None
    assert crud.ExpenseCRUD.get_expense(db, expense.id, test_user.id) is None


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

    e1 = crud.ExpenseCRUD.create_expense(db, expense1, test_user.id)
    e2 = crud.ExpenseCRUD.create_expense(db, expense2, test_user.id)
    e3 = crud.ExpenseCRUD.create_expense(db, expense3, test_user.id)

    start_date = date(2025, 9, 21)
    end_date = date(2025, 9, 27)
    expenses_in_range = crud.ExpenseCRUD.get_expenses_in_range(db, start_date, end_date, test_user.id)

    assert len(expenses_in_range) == 1
    assert expenses_in_range[0].title == "Dinner"


def test_user_crud_operations(db):
    # Test create user
    user_data = schemas.UserCreate(
        username="newuser",
        email="new@example.com",
        password="newpassword"
    )
    user = crud.UserCRUD.create_user(db, user_data)
    assert user.username == "newuser"
    assert user.email == "new@example.com"

    # Test get by username
    found_user = crud.UserCRUD.get_user_by_username(db, "newuser")
    assert found_user.id == user.id

    # Test get by email
    found_user_email = crud.UserCRUD.get_user_by_email(db, "new@example.com")
    assert found_user_email.id == user.id

    # Test authenticate user
    auth_user = crud.UserCRUD.authenticate_user(db, "newuser", "newpassword")
    assert auth_user.id == user.id

    # Test update user
    update_data = schemas.UserUpdate(username="updateduser")
    updated = crud.UserCRUD.update_user(db, user.id, update_data)
    assert updated.username == "updateduser"


def test_tag_crud_operations(db, test_user):
    # Test tag creation through expense
    expense_data = schemas.ExpenseCreate(
        title="Test Expense",
        amount=10.0,
        tags=["tag1", "tag2"],
        type="expense"
    )
    expense = crud.ExpenseCRUD.create_expense(db, expense_data, test_user.id)

    # Test that tags were created
    assert len(expense.tags) == 2
    tag_names = [tag.name for tag in expense.tags]
    assert "tag1" in tag_names
    assert "tag2" in tag_names

    # Test reusing existing tags
    expense_data2 = schemas.ExpenseCreate(
        title="Test Expense 2",
        amount=15.0,
        tags=["tag1", "tag3"],  # tag1 should be reused
        type="expense"
    )
    expense2 = crud.ExpenseCRUD.create_expense(db, expense_data2, test_user.id)

    # Verify tag reuse
    all_expenses = crud.ExpenseCRUD.get_expenses(db, test_user.id)
    assert len(all_expenses) == 2
