HEAD
# RPG Tracker

Backend-first Django project for a personal RPG progression system.

## Product idea

This is not a todo app with points. The system is meant to model a character that grows through habits, quests, XP, streaks, and achievements.

## Milestone 0 scope

- Django project scaffolded
- custom user model prepared
- DRF connected
- PostgreSQL-ready settings
- pytest and Ruff configured
- Docker files added

## Current architecture choice

- `User` handles authentication and identity
- `CharacterProfile` will handle RPG progression in the next milestone

This split is intentional: auth concerns and game-domain concerns evolve at different speeds.

## Local setup

```powershell
C:\Users\Admin\AppData\Local\Python\bin\python.exe -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .[dev]
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

## Docker setup

```powershell
docker compose up --build
```

## Next milestone

Milestone 1 will add:

- registration and login API
- automatic CharacterProfile creation
- profile endpoint
=======
# RPG_tracker
a8c0bc12f43c06e22a13e8ec8edb7d93cfa86d6d
