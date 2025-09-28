import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.models import Base

# File-based SQLite DB for testing
TEST_DB_PATH = "./data/test.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables initially
Base.metadata.create_all(bind=engine)

# Override the dependency to use the test DB
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# Fixture to reset DB before each test
@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Remove test DB file after all tests
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

# --------------------- API Tests ---------------------

def test_create_expense_api():
    response = client.post(
        "/expenses",
        json={"title": "Lunch", "amount": 12.5, "tags": ["food"], "type": "expense"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Lunch"
    assert len(data["tags"]) == 1

def test_get_expense_api():
    post = client.post("/expenses", json={"title": "Coffee", "amount": 3.0, "tags": ["drink"]})
    exp_id = post.json()["id"]

    get = client.get(f"/expenses/{exp_id}")
    assert get.status_code == 200
    assert get.json()["title"] == "Coffee"

def test_update_expense_api():
    post = client.post("/expenses", json={"title": "Book", "amount": 10, "tags": ["study"]})
    exp_id = post.json()["id"]

    put = client.put(
        f"/expenses/{exp_id}",
        json={"title": "Book Updated", "amount": 12, "tags": ["study", "fun"], "type": "expense"}
    )
    assert put.status_code == 200
    data = put.json()
    assert data["title"] == "Book Updated"
    assert len(data["tags"]) == 2

def test_delete_expense_api():
    post = client.post("/expenses", json={"title": "Snack", "amount": 5, "tags": []})
    exp_id = post.json()["id"]

    delete = client.delete(f"/expenses/{exp_id}")
    assert delete.status_code == 200

    get = client.get(f"/expenses/{exp_id}")
    assert get.status_code == 404
