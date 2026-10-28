# Smart Order & Conveyor System

A small backend with a web interface that simulates how a manufacturing system processes orders. A customer orders parts,
the system checks and reserves stock, and a background process simulates a machine assembling the order.

## Features

- Manage parts and their stock quantity
- Create orders with an atomic stock check (an order is rejected with `409` if the stock is not enough)
- Start an order: its status changes from `PENDING` to `PROCESSING` and, after a few seconds, to `READY`
- Background processing, so the API stays responsive while a machine is working
- Simple web interface that refreshes automatically

## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy
- **Database:** MySQL
- **Frontend:** HTML, CSS, vanilla JavaScript

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/parts` | Create a part |
| GET | `/parts` | List parts |
| POST | `/orders` | Create an order |
| GET | `/orders` | List orders |
| PUT | `/orders/{id}/start` | Start processing an order |

Interactive API documentation is available at `/docs`.

## Project Structure

```
frontend/     HTML, CSS and JavaScript client
database.py   Database connection and session
models.py     SQLAlchemy tables
dto.py        Request and response schemas
main.py       API endpoints and order processing
```

## Running Locally

**Requirements:** Python 3.10+, MySQL

1. Create the database:
   ```sql
   CREATE DATABASE robot_orders;
   ```
2. Create a virtual environment and install the dependencies:
   ```
   python -m venv venv
   venv\Scripts\activate
   pip install fastapi uvicorn sqlalchemy pymysql cryptography
   ```
3. Set the database credentials (PowerShell):
   ```
   $env:DB_USER='root'
   $env:DB_PASSWORD='your_password'
   ```
   Optional variables: `DB_HOST`, `DB_PORT`, `DB_NAME` (defaults: `localhost`, `3306`, `robot_orders`).
4. Start the application:
   ```
   python -m uvicorn main:app --reload
   ```
5. Open `http://127.0.0.1:8000/` for the interface or `http://127.0.0.1:8000/docs` for the API documentation.
