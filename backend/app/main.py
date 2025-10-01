# File: backend/app/main.py
from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import date, timedelta
from fastapi.middleware.cors import CORSMiddleware
import os

from app import models, schemas, crud, auth

# --- Database setup ---
data_dir = "./data"
os.makedirs(data_dir, exist_ok=True)
db_path = os.path.join(data_dir, "expenses.db")
DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

if not os.path.exists(db_path):
    models.Base.metadata.create_all(bind=engine)

# --- FastAPI app setup ---
app = FastAPI(title="Expense Manager API")

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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Auth Routes ---
@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user)

@app.post("/login", response_model=schemas.Token)
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.put("/me", response_model=schemas.User)
def update_user_profile(
    user_data: schemas.UserUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    updated_user = crud.update_user(db, current_user.id, user_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

# --- Expense Routes ---
@app.get("/expenses", response_model=list[schemas.Expense])
def list_expenses(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_expenses(db, current_user.id)

@app.post("/expenses", response_model=schemas.Expense)
def add_expense(
    expense: schemas.ExpenseCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return crud.create_expense(db, expense, current_user.id)

@app.get("/expenses/range", response_model=list[schemas.Expense])
def list_expenses_in_range(
    start_date: date = Query(..., description="Start date YYYY-MM-DD"),
    end_date: date = Query(..., description="End date YYYY-MM-DD"),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_expenses_in_range(db, start_date, end_date, current_user.id)

@app.get("/expenses/{expense_id}", response_model=schemas.Expense)
def get_expense(
    expense_id: str,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    expense = crud.get_expense(db, expense_id, current_user.id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@app.put("/expenses/{expense_id}", response_model=schemas.Expense)
def update_expense(
    expense_id: str,
    expense: schemas.ExpenseCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    updated = crud.update_expense(db, expense_id, expense, current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Expense not found")
    return updated

@app.delete("/expenses/{expense_id}", response_model=schemas.Expense)
def delete_expense(
    expense_id: str,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    deleted = crud.delete_expense(db, expense_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Expense not found")
    return deleted
