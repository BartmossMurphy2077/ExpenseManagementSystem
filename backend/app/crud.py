# File: backend/app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime, date, time

def get_expenses(db: Session):
    return db.query(models.Expense).all()

def get_expense(db: Session, expense_id: str):
    return db.query(models.Expense).filter(models.Expense.id == expense_id).first()

def create_expense(db: Session, expense: schemas.ExpenseCreate):
    tag_objects = []
    for tag_name in expense.tags:
        tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
        if not tag:
            tag = models.Tag(name=tag_name)
            db.add(tag)
        tag_objects.append(tag)

    ts = expense.timestamp
    if isinstance(ts, str):
        ts = datetime.fromisoformat(ts)  # keep full datetime
    elif ts is None:
        ts = datetime.now()  # default to now

    db_expense = models.Expense(
        title=expense.title,
        amount=expense.amount,
        timestamp=ts,
        type=expense.type,
        tags=tag_objects
    )

    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def update_expense(db: Session, expense_id: str, expense_data: schemas.ExpenseCreate):
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if not expense:
        return None
    expense.title = expense_data.title
    expense.amount = expense_data.amount
    expense.type = expense_data.type
    if expense_data.tags:
        tag_objects = []
        for tag_name in expense_data.tags:
            tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
            if not tag:
                tag = models.Tag(name=tag_name)
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

def get_expenses_in_range(db: Session, start_date: date, end_date: date):
    # convert date range to datetimes covering the whole days
    start_dt = datetime.combine(start_date, time.min)
    end_dt = datetime.combine(end_date, time.max)
    return (
        db.query(models.Expense)
        .filter(models.Expense.timestamp >= start_dt)
        .filter(models.Expense.timestamp <= end_dt)
        .all()
    )

def delete_expense(db: Session, expense_id: str):
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if expense:
        db.delete(expense)
        db.commit()
    return expense
