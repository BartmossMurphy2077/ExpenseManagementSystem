import pytest
from app import crud, schemas

def test_create_and_get_user(db_session, test_user):
    user_obj = schemas.UserCreate(**test_user)
    user = crud.create_user(db_session, user_obj)
    assert user.id
    fetched = crud.get_user_by_username(db_session, test_user["username"])
    assert fetched.id == user.id

def test_authenticate_user(db_session, test_user):
    user_obj = schemas.UserCreate(**test_user)
    crud.create_user(db_session, user_obj)
    user = crud.authenticate_user(db_session, test_user["username"], test_user["password"])
    assert user is not None
    assert user.username == test_user["username"]
    # Wrong password
    user_fail = crud.authenticate_user(db_session, test_user["username"], "wrong")
    assert user_fail is None

def test_update_user(db_session, test_user):
    user_obj = schemas.UserCreate(**test_user)
    user = crud.create_user(db_session, user_obj)
    update_data = schemas.UserUpdate(username="newname")
    updated = crud.update_user(db_session, user.id, update_data)
    assert updated.username == "newname"
