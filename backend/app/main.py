from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import date
from fastapi.middleware.cors import CORSMiddleware
import os

from app import models, schemas, crud

# --- Ensure data directory exists ---
data_dir = "./data"
os.makedirs(data_dir, exist_ok=True)

# --- Database path ---
db_path = os.path.join(data_dir, "expenses.db")
DATABASE_URL = f"sqlite:///{db_path}"

# --- Create engine and session ---
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Create tables if database does not exist ---
if not os.path.exists(db_path):
    models.Base.metadata.create_all(bind=engine)

# --- FastAPI app setup ---
app = FastAPI(title="Expense Manager API")

# Allow frontend to access backend
origins = [
    "http://localhost:3000",
    "http://frontend"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Routes ---
@app.get("/expenses", response_model=list[schemas.Expense])
def list_expenses(db: Session = Depends(get_db)):
    return crud.get_expenses(db)

@app.post("/expenses", response_model=schemas.Expense)
def add_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    return crud.create_expense(db, expense)

@app.get("/expenses/range", response_model=list[schemas.Expense])
def list_expenses_in_range(
    start_date: date = Query(..., description="Start date YYYY-MM-DD"),
    end_date: date = Query(..., description="End date YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    return crud.get_expenses_in_range(db, start_date, end_date)

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
