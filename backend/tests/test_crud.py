from app import crud, schemas

def test_create_and_get_expense(db):
    expense_data = schemas.ExpenseCreate(
        title="Coffee",
        amount=3.5,
        tags=["drink"],
        type="expense"
    )
    created = crud.create_expense(db, expense_data)
    assert created.id is not None
    assert created.title == "Coffee"
    assert len(created.tags) == 1

    fetched = crud.get_expense(db, created.id)
    assert fetched.id == created.id
    assert fetched.title == "Coffee"

def test_update_expense(db):
    expense_data = schemas.ExpenseCreate(title="Book", amount=10, tags=["study"])
    expense = crud.create_expense(db, expense_data)

    updated_data = schemas.ExpenseCreate(title="Book Updated", amount=15, tags=["study", "fun"])
    updated = crud.update_expense(db, expense.id, updated_data)

    assert updated.title == "Book Updated"
    assert updated.amount == 15
    assert len(updated.tags) == 2

def test_delete_expense(db):
    expense_data = schemas.ExpenseCreate(title="Snack", amount=5, tags=["food"])
    expense = crud.create_expense(db, expense_data)

    deleted = crud.delete_expense(db, expense.id)
    assert deleted is not None
    assert crud.get_expense(db, expense.id) is None
