[English version](README.en.md)

# RPG Tracker

Backend-first Django REST Framework проект для RPG-системы личного прогресса: пользователь, профиль персонажа, привычки, квесты, progression events, XP/level rules, streak logic, token auth и OpenAPI-документация.

## Идея проекта

Это не просто todo-list с очками.

Проект задуман как backend для системы, в которой пользователь развивает персонажа через:
- привычки;
- квесты;
- опыт;
- streaks;
- progression profile.

Сейчас проект находится в рабочем состоянии как backend foundation+, где уже есть не только CRUD, но и бизнес-логика прогресса.

## Что уже реализовано

- Django-проект с кастомной моделью пользователя
- DRF и token authentication
- регистрация пользователя
- логин пользователя
- профиль персонажа
- timezone-aware профиль персонажа
- CRUD API для привычек
- CRUD API для квестов
- completion / failure flow для привычек и квестов
- история progression events
- XP, level и streak rules
- OpenAPI schema, Swagger UI и ReDoc
- ownership-based data access
- PostgreSQL-ready конфигурация
- Docker setup
- GitHub Actions CI
- pytest и Ruff

## Текущая структура домена

- `accounts` — пользователь, auth flow, регистрация и логин
- `characters` — профиль персонажа, текущий прогресс и timezone
- `habits` — повторяемые действия пользователя
- `quests` — конкретные игровые задачи, в том числе связанные с привычками
- `progression` — события прогресса, completion/failure service layer, XP/level/streak rules

Это хорошее архитектурное решение для роста проекта:
- auth concerns живут отдельно;
- gameplay entities не смешиваются с учётной записью;
- проект можно расширять по доменам, а не в один большой `models.py`.

## Стек

- Python 3.14+
- Django 6
- Django REST Framework
- drf-spectacular
- DRF Token Auth
- PostgreSQL (`psycopg`)
- SQLite для локального быстрого старта
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

## Поведение, которое уже зафиксировано тестами

- регистрация создаёт пользователя, профиль персонажа и token
- логин возвращает существующий token
- профиль требует аутентификацию
- пользователь видит и изменяет только свой профиль
- профиль валидирует timezone как IANA timezone name
- пользователь видит только свои привычки и квесты
- нельзя получить доступ к чужой привычке
- нельзя привязать чужую привычку к своему квесту
- completion action выдаёт XP и пишет событие прогресса
- нельзя повторно завершить одну и ту же привычку в один локальный день пользователя
- fail / miss actions применяют penalty и пишут историю
- streak считается по timezone пользователя, а не только по глобальному UTC
- schema endpoint доступен и валидируется в CI

## Локальный запуск

### 1. Установка окружения

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e .[dev]
```

### 2. Переменные окружения

Создай локальный `.env` на основе `.env.example` или задай переменные окружения вручную.

### 3. Миграции

```powershell
.\.venv\Scripts\python.exe manage.py migrate
```

### 4. Создание суперпользователя

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

### 5. Запуск сервера

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

## Docker

```powershell
docker compose up --build
```

## Проверки

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe manage.py spectacular --file openapi-schema.yaml --validate
```

Локально 26 апреля 2026:
- тесты проходят: `21 passed`

## Почему проект полезен для портфолио

- показывает backend-мышление, а не только шаблонный CRUD;
- показывает разделение домена по приложениям;
- показывает auth и user-owned data access;
- показывает service layer и доменные инварианты;
- показывает DRF, OpenAPI и тесты;
- показывает, что проект уже подготовлен к PostgreSQL, Docker и CI-сценарию.

## Текущий статус

Сейчас это уже не просто foundation, а небольшой, но полноценный gameplay backend:
- есть доменные сервисы для completion/failure flow;
- есть история событий прогресса;
- есть timezone-aware streak logic;
- есть schema docs и CI.

Следующие логичные шаги:
- refresh-token / JWT strategy вместо только token auth;
- планировщик daily reset и overdue logic;
- achievements, inventory, rewards economy;
- фильтрация и пагинация history endpoint;
- frontend client или отдельная admin/game master панель.
