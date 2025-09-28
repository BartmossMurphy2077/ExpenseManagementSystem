import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app, get_db
from app.models import Base

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Override dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

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


def test_get_expenses_in_range_api():
    # Add expenses
    client.post("/expenses", json={"title": "Breakfast", "amount": 8.0, "tags": ["food"], "type": "expense",
                                   "timestamp": "2025-09-20"})
    client.post("/expenses", json={"title": "Dinner", "amount": 20.0, "tags": ["food"], "type": "expense",
                                   "timestamp": "2025-09-25"})
    client.post("/expenses",
                json={"title": "Snack", "amount": 5.0, "tags": ["food"], "type": "expense", "timestamp": "2025-09-28"})

    # Query the range
    response = client.get("/expenses/range", params={"start_date": "2025-09-21", "end_date": "2025-09-27"})

    print(response.json())  # Debug: see what is returned
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Dinner"