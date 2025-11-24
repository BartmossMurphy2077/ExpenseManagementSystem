import logging
from datetime import date, timedelta, datetime
from typing import Optional
import os

from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from prometheus_fastapi_instrumentator import Instrumentator  # optional dependency

from app import models, schemas, crud, auth
from app.database import get_db
from app.config import settings

logger = logging.getLogger(__name__)

# --- FastAPI app setup ---
app = FastAPI(title="Expense Manager API")

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://frontend",
    f"https://{os.getenv('FRONT_END_WEBAPP_NAME', '')}.azurewebsites.net"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instrumentation for Prometheus (install prometheus-fastapi-instrumentator)
@app.on_event("startup")
def startup_instrumentation():
    try:
        Instrumentator().instrument(app).expose(app, "/metrics")
        logger.info("Prometheus Instrumentator enabled at /metrics")
    except Exception as e:
        # Instrumentation is optional; do not crash app if not available
        logger.warning("Prometheus Instrumentator not enabled: %s", e)


# Create a dependency function that properly handles auth
def get_current_user_with_db(
    credentials=Depends(auth.security),
    db: Session = Depends(get_db)
) -> models.User:
    """
    Use AuthService to verify token and fetch user from DB.
    This centralizes authentication logic and improves testability.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = auth.AuthService.get_authenticated_user(db, credentials.credentials)
    if user is None:
        raise credentials_exception

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
def health(db: Session = Depends(get_db), full: Optional[bool] = Query(False, description="Run full health checks including write-test")):
    """
    Health endpoint:
      - basic DB read (SELECT 1) or SQLite file existence
      - optional write test (CREATE TEMP TABLE / DROP) if ?full=true

    Returns JSON with status and details.
    """
    from .config import settings

    details = {"timestamp": datetime.utcnow().isoformat(), "database": {"read": False, "write": "skipped"}}

    # SQLite check
    if settings.database_url.startswith("sqlite"):
        db_path = settings.database_url.replace("sqlite:///", "")
        if os.path.isfile(db_path):
            details["database"]["read"] = True
        else:
            details["database"]["read"] = False
            return {"status": "unhealthy", **details}
    else:
        # Try lightweight DB read
        try:
            db.execute("SELECT 1")
            details["database"]["read"] = True
        except Exception as e:
            logger.exception("Database read check failed: %s", e)
            details["database"]["read"] = False
            return {"status": "unhealthy", **details}

    # Optional write test
    if full:
        try:
            db.execute("CREATE TEMP TABLE IF NOT EXISTS health_check_temp (id INTEGER)")
            db.execute("DROP TABLE IF EXISTS health_check_temp")
            details["database"]["write"] = "ok"
        except Exception as e:
            logger.exception("Database write check failed: %s", e)
            details["database"]["write"] = "failed"
            return {"status": "degraded", **details}
    else:
        details["database"]["write"] = "skipped"

    return {"status": "ok", **details}

