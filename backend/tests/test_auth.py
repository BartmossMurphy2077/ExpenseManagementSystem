# backend/tests/test_auth.py
import pytest
from app.auth import AuthService
from app import models, schemas, crud
from datetime import timedelta


def test_password_hashing():
    password = "testpassword123"
    hashed = AuthService.get_password_hash(password)

    assert hashed != password
    assert AuthService.verify_password(password, hashed)
    assert not AuthService.verify_password("wrongpassword", hashed)


def test_token_creation_and_verification():
    user_id = "test-user-id"
    token = AuthService.create_access_token({"sub": user_id})

    assert token is not None
    verified_user_id = AuthService.verify_token(token)
    assert verified_user_id == user_id


def test_token_with_expiration():
    user_id = "test-user-id"
    expires_delta = timedelta(minutes=30)
    token = AuthService.create_access_token({"sub": user_id}, expires_delta)

    verified_user_id = AuthService.verify_token(token)
    assert verified_user_id == user_id


def test_invalid_token():
    invalid_token = "invalid.token.here"
    verified_user_id = AuthService.verify_token(invalid_token)
    assert verified_user_id is None


def test_get_user_by_id(db, test_user):
    found_user = AuthService.get_user_by_id(db, test_user.id)
    assert found_user.id == test_user.id
    assert found_user.username == test_user.username

    # Test with non-existent user
    not_found = AuthService.get_user_by_id(db, "non-existent-id")
    assert not_found is None


def test_user_authentication_flow(db):
    # Create user
    user_data = schemas.UserCreate(
        username="authtest",
        email="auth@test.com",
        password="testpass123"
    )
    user = crud.UserCRUD.create_user(db, user_data)

    # Test successful authentication
    auth_user = crud.UserCRUD.authenticate_user(db, "authtest", "testpass123")
    assert auth_user is not None
    assert auth_user.id == user.id

    # Test failed authentication - wrong password
    failed_auth = crud.UserCRUD.authenticate_user(db, "authtest", "wrongpass")
    assert failed_auth is None

    # Test failed authentication - wrong username
    failed_auth2 = crud.UserCRUD.authenticate_user(db, "wronguser", "testpass123")
    assert failed_auth2 is None
