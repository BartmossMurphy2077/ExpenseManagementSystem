# backend/app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas
from .auth import AuthService
from datetime import datetime, date, time
from typing import Optional, List

class UserCRUD:
    @staticmethod
    def create_user(db: Session, user: schemas.UserCreate) -> models.User:
        hashed_password = AuthService.get_password_hash(user.password)
        db_user = models.User(
            username=user.username,
            email=user.email,
            password_hash=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.username == username).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.email == email).first()

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
        user = UserCRUD.get_user_by_username(db, username)
        if not user or not AuthService.verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def update_user(db: Session, user_id: str, user_data: schemas.UserUpdate) -> Optional[models.User]:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            return None

        if user_data.username:
            user.username = user_data.username
        if user_data.email:
            user.email = user_data.email
        if user_data.password:
            user.password_hash = AuthService.get_password_hash(user_data.password)

        db.commit()
        db.refresh(user)
        return user

class ExpenseCRUD:
    @staticmethod
    def get_expenses(db: Session, user_id: str) -> List[models.Expense]:
        return db.query(models.Expense).filter(models.Expense.user_id == user_id).all()

    @staticmethod
    def get_expense(db: Session, expense_id: str, user_id: str) -> Optional[models.Expense]:
        return db.query(models.Expense).filter(
            models.Expense.id == expense_id,
            models.Expense.user_id == user_id
        ).first()

    @staticmethod
    def create_expense(db: Session, expense: schemas.ExpenseCreate, user_id: str) -> models.Expense:
        tag_objects = TagCRUD._get_or_create_tags(db, expense.tags, user_id)
        timestamp = ExpenseCRUD._parse_timestamp(expense.timestamp)

        db_expense = models.Expense(
            title=expense.title,
            amount=expense.amount,
            timestamp=timestamp,
            type=expense.type,
            user_id=user_id,
            tags=tag_objects
        )

        db.add(db_expense)
        db.commit()
        db.refresh(db_expense)
        return db_expense

    @staticmethod
    def update_expense(db: Session, expense_id: str, expense_data: schemas.ExpenseCreate, user_id: str) -> Optional[models.Expense]:
        expense = ExpenseCRUD.get_expense(db, expense_id, user_id)
        if not expense:
            return None

        expense.title = expense_data.title
        expense.amount = expense_data.amount
        expense.type = expense_data.type

        if expense_data.tags:
            expense.tags = TagCRUD._get_or_create_tags(db, expense_data.tags, user_id)

        if expense_data.timestamp is not None:
            expense.timestamp = ExpenseCRUD._parse_timestamp(expense_data.timestamp)

        db.commit()
        db.refresh(expense)
        return expense

    @staticmethod
    def get_expenses_in_range(db: Session, start_date: date, end_date: date, user_id: str) -> List[models.Expense]:
        start_dt = datetime.combine(start_date, time.min)
        end_dt = datetime.combine(end_date, time.max)
        return (
            db.query(models.Expense)
            .filter(models.Expense.user_id == user_id)
            .filter(models.Expense.timestamp >= start_dt)
            .filter(models.Expense.timestamp <= end_dt)
            .all()
        )

    @staticmethod
    def delete_expense(db: Session, expense_id: str, user_id: str) -> Optional[models.Expense]:
        expense = ExpenseCRUD.get_expense(db, expense_id, user_id)
        if expense:
            db.delete(expense)
            db.commit()
        return expense

    @staticmethod
    def _parse_timestamp(timestamp) -> datetime:
        if isinstance(timestamp, str):
            return datetime.fromisoformat(timestamp)
        elif timestamp is None:
            return datetime.now()
        return timestamp

class TagCRUD:
    @staticmethod
    def _get_or_create_tags(db: Session, tag_names: List[str], user_id: str) -> List[models.Tag]:
        tag_objects = []
        for tag_name in tag_names:
            tag = db.query(models.Tag).filter(
                models.Tag.name == tag_name,
                models.Tag.user_id == user_id
            ).first()
            if not tag:
                tag = models.Tag(name=tag_name, user_id=user_id)
                db.add(tag)
            tag_objects.append(tag)
        return tag_objects

# Backward compatibility functions
def create_user(db: Session, user: schemas.UserCreate):
    return UserCRUD.create_user(db, user)

def get_user_by_username(db: Session, username: str):
    return UserCRUD.get_user_by_username(db, username)

def get_user_by_email(db: Session, email: str):
    return UserCRUD.get_user_by_email(db, email)

def authenticate_user(db: Session, username: str, password: str):
    return UserCRUD.authenticate_user(db, username, password)

def update_user(db: Session, user_id: str, user_data: schemas.UserUpdate):
    return UserCRUD.update_user(db, user_id, user_data)

def get_expenses(db: Session, user_id: str):
    return ExpenseCRUD.get_expenses(db, user_id)

def get_expense(db: Session, expense_id: str, user_id: str):
    return ExpenseCRUD.get_expense(db, expense_id, user_id)

def create_expense(db: Session, expense: schemas.ExpenseCreate, user_id: str):
    return ExpenseCRUD.create_expense(db, expense, user_id)

def update_expense(db: Session, expense_id: str, expense_data: schemas.ExpenseCreate, user_id: str):
    return ExpenseCRUD.update_expense(db, expense_id, expense_data, user_id)

def get_expenses_in_range(db: Session, start_date: date, end_date: date, user_id: str):
    return ExpenseCRUD.get_expenses_in_range(db, start_date, end_date, user_id)

def delete_expense(db: Session, expense_id: str, user_id: str):
    return ExpenseCRUD.delete_expense(db, expense_id, user_id)
