# Expense Management System

A simple **expense management system** built for a DevOps assignment.  
Manage your expenses, track spending over time, and visualize analytics with interactive charts.

---

## Features

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
- **Containerization:** Docker & Docker Compose  

---

## Getting Started

### Prerequisites

- Docker
- Docker Compose

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