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
pytest -v
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
    participant DB as Database (SQLite)

    %% --- Login Flow ---
    U->>FE: Enter username & password
    FE->>BE: POST /login (username, password)
    BE->>DB: Verify user credentials
    DB-->>BE: User record
    BE-->>FE: JWT access_token
    FE-->>U: User logged in (token stored in client)

    %% --- Expenses Flow ---
    U->>FE: View Expenses Page
    FE->>BE: GET /expenses (Authorization: Bearer token)
    BE->>DB: Fetch expenses for current_user
    DB-->>BE: Expense list
    BE-->>FE: JSON list of expenses
    FE-->>U: Show expense list

    U->>FE: Add/Edit/Delete Expense
    FE->>BE: POST/PUT/DELETE /expenses (with Bearer token)
    BE->>DB: Create/Update/Delete expense
    DB-->>BE: Success/Updated record
    BE-->>FE: Updated expenses
    FE-->>U: UI refreshes

    %% --- Analytics Flow ---
    U->>FE: View Analytics Page
    FE->>BE: GET /expenses/range?start=...&end=... (with token)
    BE->>DB: Query expenses by user and date range
    DB-->>BE: Matching expenses
    BE-->>FE: JSON data
    FE-->>U: Render charts (bar, pie)
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
    USER ||--o{ TAG : "defines"
    EXPENSE ||--o{ EXPENSE_TAGS : "tagged with"
    TAG ||--o{ EXPENSE_TAGS : "applies to"
```