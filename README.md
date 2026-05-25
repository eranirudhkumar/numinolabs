# Neighborhood Library Service

A full-stack library management application built with **Python / FastAPI**, **PostgreSQL**, and **Next.js**.

---

## Architecture

```
┌──────────────┐       REST/HTTP      ┌────────────────────┐      SQL      ┌──────────────┐
│  Next.js UI  │ ──────────────────▶  │  FastAPI Backend    │ ───────────▶  │  PostgreSQL  │
│  (port 3000) │                      │  (port 8000)        │               │  (port 5432) │
└──────────────┘                      └────────────────────┘               └──────────────┘
```

Service contract is defined in [`backend/proto/library.proto`](backend/proto/library.proto).

---

## Quick Start (Docker — Recommended)

### Prerequisites
- Docker ≥ 24 and Docker Compose v2

```bash
# Clone / enter the project
cd numinolabs

# Start everything (DB + backend + frontend)
docker compose up --build
```

| Service  | URL |
|----------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger docs | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

The PostgreSQL schema is applied automatically from `backend/migrations/init.sql` on first boot.

---

## Local Development (Without Docker)

### 1. PostgreSQL Setup

```bash
# Create the database and user
psql -U postgres <<SQL
CREATE USER library_user WITH PASSWORD 'library_pass';
CREATE DATABASE library_db OWNER library_user;
\c library_db
\i backend/migrations/init.sql
SQL
```

### 2. Backend Setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env if your DB credentials differ

# Start the server (hot-reload in dev)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure API URL
cp .env.local.example .env.local   # or just use the existing .env.local

# Start the dev server
npm run dev
```

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://library_user:library_pass@localhost:5432/library_db` | PostgreSQL connection string |
| `FINE_PER_DAY` | `0.50` | Fine amount (USD) per overdue day |
| `LOAN_PERIOD_DAYS` | `14` | Standard loan duration in days |
| `APP_ENV` | `development` | `development` or `production` |

### Frontend (`frontend/.env.local`)

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000/api/v1` | Backend API base URL |

---

## API Reference

Full interactive docs at **http://localhost:8000/docs**

### Books — `/api/v1/books`

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/books` | Create a new book |
| `GET` | `/books` | List books (paginated, filterable by title, author, and genre) |
| `GET` | `/books/{id}` | Get a single book |
| `PATCH` | `/books/{id}` | Partial update a book |

### Members — `/api/v1/members`

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/members` | Register a new member |
| `GET` | `/members` | List all members (paginated) |
| `GET` | `/members/{id}` | Get a single member |
| `PATCH` | `/members/{id}` | Partial update a member |

### Loans — `/api/v1/loans`

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/loans/borrow` | Borrow a book |
| `POST` | `/loans/{id}/return` | Return a borrowed book |
| `GET` | `/loans` | List all loans (paginated) |
| `GET` | `/loans/member/{id}` | All loans for a member |
| `GET` | `/loans/overdue` | All currently overdue loans |

---

## Protocol Buffer Contract

The service interface is formally defined in [`backend/proto/library.proto`](backend/proto/library.proto).

To compile the proto (if you want to use the gRPC client SDK):

```bash
pip install grpcio-tools

python -m grpc_tools.protoc \
  -I backend/proto \
  --python_out=backend/app \
  --grpc_python_out=backend/app \
  backend/proto/library.proto
```

---

## Database Schema

```
books
  id UUID PK, isbn VARCHAR unique, title VARCHAR, author VARCHAR,
  genre VARCHAR, published_year SMALLINT,
  total_copies INT, available_copies INT,
  created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ

members
  id UUID PK, first_name VARCHAR, last_name VARCHAR, email VARCHAR unique,
  phone VARCHAR, address TEXT,
  membership_status ENUM(active|suspended|expired), membership_date DATE,
  created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ

loans
  id UUID PK,
  book_id UUID FK→books.id, member_id UUID FK→members.id,
  borrowed_at TIMESTAMPTZ, due_date TIMESTAMPTZ, returned_at TIMESTAMPTZ,
  status ENUM(active|returned|overdue), fine_amount NUMERIC(10,2),
  created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ
```

---

## Sample Client Script

See [`backend/sample_client.py`](backend/sample_client.py) — demonstrates the full borrow/return cycle via `httpx`.

```bash
cd backend
python sample_client.py
```

---

## Key Business Rules

1. **Availability** — a book cannot be borrowed if `available_copies == 0` (HTTP 409)
2. **Membership** — only members with `active` status can borrow (HTTP 403)
3. **Due date** — set to `borrowed_at + LOAN_PERIOD_DAYS` (default 14 days)
4. **Fines** — calculated at return time: `days_late × FINE_PER_DAY` (default $0.50/day)
5. **Duplicate ISBN** — rejected with HTTP 409
6. **Duplicate email** — rejected with HTTP 409

---

## Project Structure

```
numinolabs/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app, CORS, router registration
│   │   ├── config.py        # Pydantic settings (reads .env)
│   │   ├── database.py      # Async SQLAlchemy engine + session
│   │   ├── models/          # ORM models (Book, Member, Loan)
│   │   ├── schemas/         # Pydantic request/response models
│   │   ├── crud/            # DB operation functions
│   │   └── routers/         # FastAPI route handlers
│   ├── proto/
│   │   └── library.proto    # gRPC / Protobuf service contract
│   ├── migrations/
│   │   └── init.sql         # PostgreSQL schema DDL
│   ├── sample_client.py     # Demo script
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/                 # Next.js App Router pages
│   ├── components/          # Shared UI components
│   ├── lib/                 # API client + TypeScript types
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```
