# File: backend/app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas, auth
from datetime import datetime, date, time


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user or not auth.verify_password(password, user.password_hash):
        return False
    return user


def update_user(db: Session, user_id: str, user_data: schemas.UserUpdate):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None

    if user_data.username:
        user.username = user_data.username
    if user_data.email:
        user.email = user_data.email
    if user_data.password:
        user.password_hash = auth.get_password_hash(user_data.password)

    db.commit()
    db.refresh(user)
    return user


def get_expenses(db: Session, user_id: str):
    return db.query(models.Expense).filter(models.Expense.user_id == user_id).all()


def get_expense(db: Session, expense_id: str, user_id: str):
    return db.query(models.Expense).filter(
        models.Expense.id == expense_id,
        models.Expense.user_id == user_id
    ).first()


def create_expense(db: Session, expense: schemas.ExpenseCreate, user_id: str):
    tag_objects = []
    for tag_name in expense.tags:
        tag = db.query(models.Tag).filter(
            models.Tag.name == tag_name,
            models.Tag.user_id == user_id
        ).first()
        if not tag:
            tag = models.Tag(name=tag_name, user_id=user_id)
            db.add(tag)
        tag_objects.append(tag)

    ts = expense.timestamp
    if isinstance(ts, str):
        ts = datetime.fromisoformat(ts)
    elif ts is None:
        ts = datetime.now()

    db_expense = models.Expense(
        title=expense.title,
        amount=expense.amount,
        timestamp=ts,
        type=expense.type,
        user_id=user_id,
        tags=tag_objects
    )

    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def update_expense(db: Session, expense_id: str, expense_data: schemas.ExpenseCreate, user_id: str):
    expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id,
        models.Expense.user_id == user_id
    ).first()
    if not expense:
        return None

    expense.title = expense_data.title
    expense.amount = expense_data.amount
    expense.type = expense_data.type

    if expense_data.tags:
        tag_objects = []
        for tag_name in expense_data.tags:
            tag = db.query(models.Tag).filter(
                models.Tag.name == tag_name,
                models.Tag.user_id == user_id
            ).first()
            if not tag:
                tag = models.Tag(name=tag_name, user_id=user_id)
                db.add(tag)
            tag_objects.append(tag)
        expense.tags = tag_objects

    if expense_data.timestamp is not None:
        ts = expense_data.timestamp
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        expense.timestamp = ts

    db.commit()
    db.refresh(expense)
    return expense


def get_expenses_in_range(db: Session, start_date: date, end_date: date, user_id: str):
    start_dt = datetime.combine(start_date, time.min)
    end_dt = datetime.combine(end_date, time.max)
    return (
        db.query(models.Expense)
        .filter(models.Expense.user_id == user_id)
        .filter(models.Expense.timestamp >= start_dt)
        .filter(models.Expense.timestamp <= end_dt)
        .all()
    )


def delete_expense(db: Session, expense_id: str, user_id: str):
    expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id,
        models.Expense.user_id == user_id
    ).first()
    if expense:
        db.delete(expense)
        db.commit()
    return expense
