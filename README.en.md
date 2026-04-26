[Русская версия](README.md)

# RPG Tracker

Backend-first Django REST Framework project for an RPG-style personal progression system with token auth, character profile, habits, quests, progression events, XP/level rules, streak logic, and OpenAPI docs.

## Product idea

This is not just a todo app with points.

The goal is to build a backend for a progression system where the user develops a character through:
- habits;
- quests;
- experience;
- streaks;
- profile progression.

At the current stage, the project already works as a backend foundation+ with real progression business logic, not only CRUD endpoints.

## What is already implemented

- Django project with a custom user model
- DRF and token authentication
- user registration
- user login
- character profile endpoint
- timezone-aware character profile
- habits CRUD API
- quests CRUD API
- completion / failure flow for habits and quests
- progression event history
- XP, level, and streak rules
- OpenAPI schema, Swagger UI, and ReDoc
- ownership-based data access
- PostgreSQL-ready configuration
- Docker setup
- GitHub Actions CI
- pytest and Ruff

## Current domain structure

- `accounts` — user model, registration, and login flow
- `characters` — character profile, current progression state, and timezone
- `habits` — repeated user behaviors
- `quests` — concrete game-like tasks, optionally linked to habits
- `progression` — progression events, completion/failure service layer, XP/level/streak rules

This structure is useful for future growth:
- auth concerns stay separate;
- gameplay entities do not leak into the account layer;
- the project can grow by domain instead of collapsing into one large module.

## Stack

- Python 3.14+
- Django 6
- Django REST Framework
- drf-spectacular
- DRF Token Auth
- PostgreSQL (`psycopg`)
- SQLite for a fast local start
- Docker / Docker Compose
- GitHub Actions
- pytest
- Ruff

## API overview

### Auth

- `POST /api/auth/register/`
- `POST /api/auth/login/`

### Profile

- `GET /api/profile/`
- `PATCH /api/profile/`

### Habits

- `GET /api/habits/`
- `POST /api/habits/`
- `GET /api/habits/{id}/`
- `PATCH /api/habits/{id}/`
- `DELETE /api/habits/{id}/`
- `POST /api/habits/{id}/complete/`
- `POST /api/habits/{id}/miss/`

### Quests

- `GET /api/quests/`
- `POST /api/quests/`
- `GET /api/quests/{id}/`
- `PATCH /api/quests/{id}/`
- `DELETE /api/quests/{id}/`
- `POST /api/quests/{id}/complete/`
- `POST /api/quests/{id}/fail/`

### Progress

- `GET /api/progress/events/`

### Schema

- `GET /api/schema/`
- `GET /api/schema/swagger-ui/`
- `GET /api/schema/redoc/`

## Behavior already covered by tests

- registration creates the user, character profile, and token
- login returns an existing token
- profile requires authentication
- a user can view and update only their own profile
- profile timezone is validated as an IANA timezone name
- a user sees only their own habits and quests
- foreign habits are not accessible
- a foreign habit cannot be attached to the user's quest
- completion actions award XP and create progression events
- the same habit cannot be completed twice in the same local user day
- fail / miss actions apply penalties and create history records
- streaks are calculated using the user's timezone, not only global UTC
- schema endpoints are available and validated in CI

## Local setup

### 1. Install the environment

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .[dev]
```

### 2. Environment variables

Create a local `.env` from `.env.example` or set the variables manually.

### 3. Run migrations

```powershell
.\.venv\Scripts\python.exe manage.py migrate
```

### 4. Create a superuser

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

### 5. Run the server

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

## Docker

```powershell
docker compose up --build
```

## Checks

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe manage.py spectacular --file openapi-schema.yaml --validate
```

Local verification on April 26, 2026:
- tests pass: `21 passed`

## Why this project is useful in a portfolio

- it shows backend thinking beyond a trivial CRUD demo;
- it shows domain separation;
- it shows auth and user-owned data access;
- it shows a service layer and domain invariants;
- it shows DRF, OpenAPI, and tests;
- it shows a backend that is already prepared for PostgreSQL, Docker, and CI.

## Current status

At the moment, this is already more than a foundation project:
- it has domain services for completion/failure flow;
- it has progression event history;
- it has timezone-aware streak logic;
- it has schema docs and CI.

Reasonable next steps:
- move from token auth to a refresh-token / JWT strategy;
- add a daily reset scheduler and overdue logic;
- introduce achievements, inventory, and reward economy;
- add filtering and pagination for the history endpoint;
- build a frontend client or a separate admin / game master panel.
