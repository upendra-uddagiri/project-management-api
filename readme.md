# Project Management API

A production-ready RESTful API built with **FastAPI** for managing projects, tasks, teams, and collaboration. Features JWT authentication, role-based access control, async database operations, file uploads, email notifications, rate limiting, and request logging.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Database Migrations](#database-migrations)
- [Running the Server](#running-the-server)
- [API Reference](#api-reference)
- [Authentication](#authentication)
- [Task Filtering & Sorting](#task-filtering--sorting)
- [File Uploads](#file-uploads)
- [Rate Limiting](#rate-limiting)

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | FastAPI |
| Database | SQLite (dev) / PostgreSQL (prod) |
| ORM | SQLAlchemy (async) |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Authentication | JWT (python-jose) |
| Password Hashing | Passlib / bcrypt |
| Email | smtplib / Gmail SMTP |
| Rate Limiting | SlowAPI |
| File Storage | Local disk |

---

## Project Structure

```
project_management_api/
│
├── app/
│   ├── main.py                  # FastAPI app, middleware, routers
│   ├── config.py                # Settings from .env
│   ├── database.py              # Async engine and session factory
│   ├── dependencies.py          # get_db, get_current_user, require_role
│   │
│   ├── models/
│   │   ├── user.py              # User model + UserRole enum
│   │   ├── project.py           # Project + ProjectMember models
│   │   ├── task.py              # Task model + TaskStatus enum
│   │   └── comment.py           # Comment model
│   │
│   ├── schemas/
│   │   ├── user.py              # UserCreate, UserRead, UserUpdate
│   │   ├── project.py           # ProjectCreate, ProjectRead, ProjectUpdate
│   │   ├── task.py              # TaskCreate, TaskRead, TaskUpdate
│   │   └── comment.py           # CommentCreate, CommentRead
│   │
│   ├── routers/
│   │   ├── auth.py              # /auth/register, /login, /refresh
│   │   ├── users.py             # /users/me, /users/{id}, /users
│   │   ├── projects.py          # /projects + /tasks under projects
│   │   ├── tasks.py             # /tasks CRUD + assign + attachments
│   │   └── comments.py          # /comments CRUD
│   │
│   ├── services/
│   │   └── task_service.py      # Email notification logic
│   │
│   ├── core/
│   │   ├── security.py          # JWT + password hashing
│   │   ├── exceptions.py        # Custom exceptions + handlers
│   │   └── middleware.py        # Logging middleware + rate limiter
│   │
│   └── utils/
│       └── pagination.py        # Pagination helper
│
├── alembic/                     # Migration files
├── uploads/                     # Uploaded file attachments
├── tests/                       # Test suite
├── .env                         # Environment variables (not committed)
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- pip

### Installation

**1. Clone the repository**
```bash
git clone <your_repo_url>
cd project_management_api
```

**2. Create and activate a virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up environment variables**

Create a `.env` file in the project root (see [Environment Variables](#environment-variables)).

**5. Run database migrations**
```bash
alembic upgrade head
```

**6. Start the development server**
```bash
uvicorn app.main:app --reload
```

**7. Open the interactive API docs**
```
http://localhost:8000/docs
```

---

## Environment Variables

Create a `.env` file at the project root with the following values:

```env
# Database
DATABASE_URL=sqlite+aiosqlite:///./project_management.db

# JWT
SECRET_KEY=your_random_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# App
APP_NAME=Project Management API
APP_VERSION=1.0.0
DEBUG=True

# Email (Gmail SMTP)
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_gmail_app_password
```

> **Note:** For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833) — not your regular Gmail password. Go to Google Account → Security → 2-Step Verification → App Passwords.

> **Production:** Switch `DATABASE_URL` to a PostgreSQL URL: `postgresql+asyncpg://user:password@localhost:5432/dbname`

---

## Database Migrations

```bash
# Apply all migrations
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "your migration message"

# Rollback one migration
alembic downgrade -1
```

---

## Running the Server

```bash
# Development (auto-reload on file changes)
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## API Reference

### Auth

| Method | Endpoint | Auth Required | Description |
|--------|----------|:---:|-------------|
| POST | `/auth/register` | No | Register a new user |
| POST | `/auth/login` | No | Login and receive tokens |
| POST | `/auth/refresh` | No | Get a new access token |

> **Rate limited:** `/auth/register` and `/auth/login` are limited to **5 requests per minute** per IP.

---

### Users

| Method | Endpoint | Auth Required | Role | Description |
|--------|----------|:---:|------|-------------|
| GET | `/users/me` | Yes | Any | Get your own profile |
| PATCH | `/users/me` | Yes | Any | Update your profile |
| GET | `/users/{user_id}` | Yes | Admin | Get any user by ID |
| GET | `/users` | Yes | Admin | List all users (paginated) |

---

### Projects

| Method | Endpoint | Auth Required | Description |
|--------|----------|:---:|-------------|
| POST | `/projects/` | Yes | Create a new project |
| GET | `/projects/` | Yes | List your projects (paginated) |
| GET | `/projects/{project_id}` | Yes | Get a project by ID |
| PATCH | `/projects/{project_id}` | Yes | Update a project |
| DELETE | `/projects/{project_id}` | Yes | Delete a project |
| POST | `/projects/{project_id}/members` | Yes | Add a member to a project |
| DELETE | `/projects/{project_id}/members/{user_id}` | Yes | Remove a member |

---

### Tasks

| Method | Endpoint | Auth Required | Description |
|--------|----------|:---:|-------------|
| POST | `/projects/{project_id}/tasks` | Yes | Create a task under a project |
| GET | `/projects/{project_id}/tasks` | Yes | List tasks (filterable, sortable, paginated) |
| GET | `/tasks/{task_id}` | Yes | Get a task by ID |
| PATCH | `/tasks/{task_id}` | Yes | Update a task |
| DELETE | `/tasks/{task_id}` | Yes | Delete a task |
| POST | `/tasks/{task_id}/assign` | Yes | Assign a task to a user |
| POST | `/tasks/{task_id}/attachments` | Yes | Upload a file attachment |

---

### Comments

| Method | Endpoint | Auth Required | Description |
|--------|----------|:---:|-------------|
| POST | `/tasks/{task_id}/comments` | Yes | Add a comment to a task |
| GET | `/tasks/{task_id}/comments` | Yes | List all comments on a task |
| DELETE | `/comments/{comment_id}` | Yes | Delete a comment (author only) |

---

## Authentication

All endpoints except `/auth/register` and `/auth/login` require a valid Bearer token in the request header:

```
Authorization: Bearer <your_access_token>
```

### Token Flow

```
1. POST /auth/register   → create account
2. POST /auth/login      → receive access_token + refresh_token
3. Use access_token      → include in Authorization header
4. POST /auth/refresh    → exchange refresh_token for new access_token
```

### Roles

| Role | Permissions |
|------|-------------|
| `member` | Default role. Can create/manage own projects and tasks |
| `manager` | Same as member (extended in future) |
| `admin` | Full access. Can view and manage all users |

> To make a user an admin, update their role directly in the database.

---

## Task Filtering & Sorting

`GET /projects/{project_id}/tasks` supports the following query parameters:

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `status` | string | Filter by task status | `?status=in_progress` |
| `assignee_id` | string | Filter by assigned user | `?assignee_id=<uuid>` |
| `due_date_from` | datetime | Tasks due after this date | `?due_date_from=2024-01-01` |
| `due_date_to` | datetime | Tasks due before this date | `?due_date_to=2024-12-31` |
| `sort_by` | string | Field to sort by | `?sort_by=due_date` |
| `order` | string | `asc` or `desc` | `?order=desc` |
| `page` | int | Page number (default: 1) | `?page=2` |
| `page_size` | int | Results per page (default: 10) | `?page_size=5` |

### Task Statuses

- `todo` — not started (default)
- `in_progress` — currently being worked on
- `in_review` — awaiting review
- `done` — completed

### Example Combined Query

```
GET /projects/{id}/tasks?status=in_progress&sort_by=due_date&order=asc&page=1&page_size=10
```

---

## File Uploads

Files are uploaded to `POST /tasks/{task_id}/attachments` as multipart form data.

- Uploaded files are stored in the `uploads/` directory with a unique UUID-based filename
- Files are accessible via `GET /uploads/<filename>`
- Supported file types: any

### Example Response

```json
{
  "original_filename": "design.pdf",
  "saved_filename": "a1b2c3d4-e5f6-...-design.pdf",
  "url": "/uploads/a1b2c3d4-e5f6-...-design.pdf",
  "size_bytes": 204800
}
```

---

## Rate Limiting

The following endpoints are rate limited to protect against brute force attacks:

| Endpoint | Limit |
|----------|-------|
| `POST /auth/register` | 5 requests / minute / IP |
| `POST /auth/login` | 5 requests / minute / IP |

Exceeding the limit returns `429 Too Many Requests`.

---

## Request Logging

Every request is logged to the terminal in the following format:

```
[POST] /auth/login -> 200 (45.23ms)
[GET]  /users/me   -> 200 (12.11ms)
[GET]  /tasks/abc  -> 404 (8.45ms)
```

---

## Error Responses

All errors follow a consistent format:

```json
{
  "detail": "Error message here"
}
```

| Status Code | Meaning |
|-------------|---------|
| 400 | Bad request (e.g. duplicate email, already a member) |
| 401 | Unauthorized (missing or invalid token) |
| 403 | Forbidden (authenticated but not permitted) |
| 404 | Resource not found |
| 422 | Validation error (invalid request body) |
| 429 | Too many requests (rate limited) |

---

## License

This project is open source and available under the [MIT License](LICENSE).