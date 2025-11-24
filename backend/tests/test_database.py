import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import crud, models, schemas
from app.models import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_create_user_success(db):
    user_in = schemas.UserCreate(username="testuser", email="test@example.com", password="password")
    user = crud.create_user(db, user_in)
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.password_hash is not None


def test_create_user_invalid_email(db):
    with pytest.raises(ValueError):
        schemas.UserCreate(username="test", email="invalid-email", password="pass")


def test_get_user_by_username(db):
    user_in = schemas.UserCreate(username="alice", email="alice@example.com", password="pass")
    crud.create_user(db, user_in)
    user = crud.get_user_by_username(db, "alice")
    assert user is not None
    assert user.username == "alice"


def test_authenticate_user(db):
    user_in = schemas.UserCreate(username="bob", email="bob@example.com", password="secret")
    crud.create_user(db, user_in)
    user = crud.authenticate_user(db, "bob", "secret")
    assert user is not None
    assert user.username == "bob"
    user_fail = crud.authenticate_user(db, "bob", "wrong")
    assert user_fail is None


def test_update_user(db):
    user_in = schemas.UserCreate(username="carol", email="carol@example.com", password="pass")
    user = crud.create_user(db, user_in)
    update_data = schemas.UserUpdate(username="carol_new", email="carol_new@example.com")
    updated_user = crud.update_user(db, user.id, update_data)
    assert updated_user.username == "carol_new"
    assert updated_user.email == "carol_new@example.com"


def test_create_expense(db):
    user_in = schemas.UserCreate(username="dave", email="dave@example.com", password="pass")
    user = crud.create_user(db, user_in)
    expense_in = schemas.ExpenseCreate(title="Lunch", amount=10.5, tags=["food"])
    expense = crud.create_expense(db, expense_in, user.id)
    assert expense.title == "Lunch"
    assert expense.amount == 10.5
    assert expense.user_id == user.id
    assert len(expense.tags) == 1
    assert expense.tags[0].name == "food"


def test_get_expenses(db):
    user_in = schemas.UserCreate(username="eve", email="eve@example.com", password="pass")
    user = crud.create_user(db, user_in)
    crud.create_expense(db, schemas.ExpenseCreate(title="Coffee", amount=3), user.id)
    crud.create_expense(db, schemas.ExpenseCreate(title="Book", amount=15), user.id)
    expenses = crud.get_expenses(db, user.id)
    assert len(expenses) == 2


def test_update_expense(db):
    user_in = schemas.UserCreate(username="frank", email="frank@example.com", password="pass")
    user = crud.create_user(db, user_in)
    expense = crud.create_expense(db, schemas.ExpenseCreate(title="Snack", amount=5), user.id)
    updated = crud.update_expense(db, expense.id, schemas.ExpenseCreate(title="Snack2", amount=6), user.id)
    assert updated.title == "Snack2"
    assert updated.amount == 6


def test_delete_expense(db):
    user_in = schemas.UserCreate(username="grace", email="grace@example.com", password="pass")
    user = crud.create_user(db, user_in)
    expense = crud.create_expense(db, schemas.ExpenseCreate(title="Tea", amount=2), user.id)
    deleted = crud.delete_expense(db, expense.id, user.id)
    assert deleted.id == expense.id
    expenses = crud.get_expenses(db, user.id)
    assert all(e.id != expense.id for e in expenses)
