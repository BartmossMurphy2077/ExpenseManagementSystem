from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from . import models, schemas, crud
import os

# SQLite DB path (inside container)
db_path = os.environ.get("SQLITE_DB_PATH", "./data/expenses.db")
DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expense Manager API")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/expenses", response_model=list[schemas.Expense])
def list_expenses(db: Session = Depends(get_db)):
    return crud.get_expenses(db)

@app.post("/expenses", response_model=schemas.Expense)
def add_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    return crud.create_expense(db, expense)

@app.get("/expenses/{expense_id}", response_model=schemas.Expense)
def get_expense(expense_id: str, db: Session = Depends(get_db)):
    expense = crud.get_expense(db, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@app.put("/expenses/{expense_id}", response_model=schemas.Expense)
def update_expense(expense_id: str, expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    updated = crud.update_expense(db, expense_id, expense)
    if not updated:
        raise HTTPException(status_code=404, detail="Expense not found")
    return updated

@app.delete("/expenses/{expense_id}", response_model=schemas.Expense)
def delete_expense(expense_id: str, db: Session = Depends(get_db)):
    deleted = crud.delete_expense(db, expense_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Expense not found")
    return deleted
