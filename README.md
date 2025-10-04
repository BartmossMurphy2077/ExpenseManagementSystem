# Expense Management System

A simple **expense management system** built for a DevOps assignment.  
Manage your expenses, track spending over time, and visualize analytics with interactive charts.

---

## Features

- User authentication:
  - Sign up, log in, and log out
  - User-specific data is saved and persisted
- Add, edit, and delete expenses
- Tag expenses for better categorization
- View analytics:
  - Monthly spending bar chart
  - Spending distribution per tag (pie chart)
- Responsive and modern UI

---

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy, SQLite  
- **Frontend:** React, Vite, Chart.js  
- **Authentication:** JWT (JSON Web Tokens) with bcrypt password hashing  
- **Containerization:** Docker & Docker Compose  

---

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Configure environment variables:**
   ```bash
   cd ExpenseManagementSystem/backend
   cp .env.example .env
   ```
- Modify `.env` as needed (e.g., change `SECRET_KEY` for JWT)

### Running tests
```bash
cd ExpenseManagementSystem/backend
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
pytest -v --cov
```
### Running the Application
- To run:
```bash
cd ExpenseManagementSystem
docker-compose up --build -d
```
- To turn off:

```bash
docker-compose down
```

## Diagrams

### Sequence Diagram
```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend (React)
    participant BE as Backend (FastAPI)
    participant DB as Database (SQLite/Postgres)

    %% --- Register Flow ---
    U->>FE: Enter username, email, password
    FE->>BE: POST /register
    BE->>DB: Insert new user (hashed password)
    DB-->>BE: New User
    BE-->>FE: User created
    FE-->>U: Registration successful

    %% --- Login Flow ---
    U->>FE: Enter username & password
    FE->>BE: POST /login
    BE->>DB: Verify user credentials
    DB-->>BE: User record
    BE-->>FE: JWT access_token
    FE-->>U: Store token locally

    %% --- Authenticated Request (expenses example) ---
    U->>FE: Open Expenses page
    FE->>BE: GET /expenses (Authorization: Bearer <token>)
    BE->>BE: Verify JWT (AuthService.verify_token)
    BE->>DB: Fetch expenses for user_id from token
    DB-->>BE: Expense list
    BE-->>FE: JSON list of expenses
    FE-->>U: Display expenses

    %% --- CRUD Expense ---
    U->>FE: Add/Edit/Delete Expense
    FE->>BE: POST/PUT/DELETE /expenses (Bearer token)
    BE->>BE: Verify JWT
    BE->>DB: Apply changes
    DB-->>BE: Success / updated record
    BE-->>FE: Updated expense data
    FE-->>U: UI updates

    %% --- Analytics ---
    U->>FE: View Analytics
    FE->>BE: GET /expenses/range (Bearer token)
    BE->>BE: Verify JWT
    BE->>DB: Query expenses by date range
    DB-->>BE: Matching expenses
    BE-->>FE: JSON stats
    FE-->>U: Charts (bar, pie)

```
### ER Diagram
```mermaid
erDiagram
    USER {
        string id PK
        string username
        string email
        string password_hash
        datetime created_at
    }

    EXPENSE {
        string id PK
        string title
        float amount
        datetime timestamp
        string type
        string user_id FK
    }

    TAG {
        string id PK
        string name
        string user_id FK
    }

    EXPENSE_TAGS {
        string expense_id FK
        string tag_id FK
    }

    USER ||--o{ EXPENSE : "owns"
    USER ||--o{ TAG : "creates"
    EXPENSE ||--o{ EXPENSE_TAGS : "can have"
    TAG ||--o{ EXPENSE_TAGS : "associated with"
```