from app import models
from datetime import datetime

def test_user_model_attributes():
    u = models.User(username="a", email="a@example.com", password_hash="hash")
    assert hasattr(u, "username")
    assert hasattr(u, "email")
