import logging
from datetime import date, timedelta, datetime
from typing import Optional
import os

from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import models, schemas, crud, auth
from app.database import get_db
from app.config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Expense Manager API")

# ✅ RESTORED YOUR ORIGINAL CORS ORIGINS
origins = [
    "http://localhost:3000",
    "http://frontend",
    "https://frontend-expensemanagement-fnh4bud6h0hjdfg9.westeurope-01.azurewebsites.net",
    "https://backend-expensemanagement-chgae9auc4b4hfh7.westeurope-01.azurewebsites.net"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Initialize Prometheus BEFORE startup event (fixes middleware timing error)
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    Instrumentator().instrument(app).expose(app, "/metrics")
    logger.info("✅ Prometheus enabled at /metrics")
except ImportError:
    logger.info("⚠️ Prometheus not installed, skipping instrumentation")
except Exception as e:
    logger.warning(f"⚠️ Prometheus setup failed: {e}")


@app.on_event("startup")
def startup_event():
    """Initialize database on startup"""
    from app.database import engine
    from app.models import Base

    logger.info(f"Initializing database at {settings.database_url}")

    # Ensure directory exists (critical for Azure)
    db_path = settings.database_url.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        logger.info(f"Created database directory: {db_dir}")

    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_current_user_with_db(
        credentials=Depends(auth.security),
        db: Session = Depends(get_db)
) -> models.User:
    """Dependency that returns authenticated user with database session."""
    user = auth.AuthService.get_authenticated_user(db, credentials.credentials)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# --- Auth Routes ---
@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    try:
        return crud.create_user(db, user)
    except Exception as e:
        logger.exception("Failed to create user: %s", e)
        raise HTTPException(status_code=500, detail="Failed to create user")


@app.post("/login", response_model=schemas.Token)
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth.create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user_with_db)):
    return current_user


@app.put("/me", response_model=schemas.User)
def update_user_profile(
        user_data: schemas.UserUpdate,
        current_user: models.User = Depends(get_current_user_with_db),
        db: Session = Depends(get_db)
):
    updated_user = crud.update_user(db, current_user.id, user_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


# --- Expense Routes ---
@app.get("/expenses", response_model=list[schemas.Expense])
def list_expenses(
        current_user: models.User = Depends(get_current_user_with_db),
        db: Session = Depends(get_db)
):
    return crud.get_expenses(db, current_user.id)


@app.post("/expenses", response_model=schemas.Expense)
def add_expense(
        expense: schemas.ExpenseCreate,
        current_user: models.User = Depends(get_current_user_with_db),
        db: Session = Depends(get_db)
):
    return crud.create_expense(db, expense, current_user.id)


@app.get("/expenses/range", response_model=list[schemas.Expense])
def list_expenses_in_range(
        start_date: date = Query(..., description="Start date YYYY-MM-DD"),
        end_date: date = Query(..., description="End date YYYY-MM-DD"),
        current_user: models.User = Depends(get_current_user_with_db),
        db: Session = Depends(get_db)
):
    return crud.get_expenses_in_range(db, start_date, end_date, current_user.id)


@app.get("/expenses/{expense_id}", response_model=schemas.Expense)
def get_expense(
        expense_id: str,
        current_user: models.User = Depends(get_current_user_with_db),
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
        current_user: models.User = Depends(get_current_user_with_db),
        db: Session = Depends(get_db)
):
    updated = crud.update_expense(db, expense_id, expense, current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Expense not found")
    return updated


@app.delete("/expenses/{expense_id}", response_model=schemas.Expense)
def delete_expense(
        expense_id: str,
        current_user: models.User = Depends(get_current_user_with_db),
        db: Session = Depends(get_db)
):
    deleted = crud.delete_expense(db, expense_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Expense not found")
    return deleted


# --- Health check ---
@app.get("/health", tags=["Health"])
def health(db: Session = Depends(get_db), full: Optional[bool] = Query(False)):
    """Health endpoint with database verification."""
    from sqlalchemy import inspect

    details = {
        "timestamp": datetime.utcnow().isoformat(),
        "database": {"read": False, "write": "skipped", "tables": []}
    }

    try:
        inspector = inspect(db.bind)
        table_names = inspector.get_table_names()
        details["database"]["tables"] = table_names
        details["database"]["read"] = len(table_names) > 0
        logger.info(f"Database health check: found {len(table_names)} tables")
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Database not healthy: {str(e)}")

    if full:
        try:
            test_user = models.User(
                username=f"health_test_{datetime.utcnow().timestamp()}",
                email=f"test_{datetime.utcnow().timestamp()}@example.com",
                password_hash="test"
            )
            db.add(test_user)
            db.flush()
            db.rollback()
            details["database"]["write"] = "ok"
            logger.info("Database write test passed")
        except Exception as e:
            logger.error(f"Database write test failed: {e}")
            details["database"]["write"] = f"failed: {str(e)}"
            raise HTTPException(status_code=503, detail=f"Database write failed: {str(e)}")

    return {"status": "ok", **details}
