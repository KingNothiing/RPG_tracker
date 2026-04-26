# Quest RPG Backend Plan

## Working title

- QuestRPG API
- Habit Kingdom API
- Discipline Engine

Use a temporary name first. Rename later when the concept becomes sharper.

## Product idea

This is not a todo app with points.

This is a backend for a personal RPG system where a user:

- creates habits and quests;
- completes daily and one-time actions;
- gains experience and levels up;
- builds streaks;
- unlocks achievements;
- receives rewards or penalties;
- progresses a character through a rule-based system.

The technical goal is to show real backend thinking:

- domain modeling;
- business rules;
- transaction safety;
- API design;
- background jobs;
- testing of critical logic;
- clear project evolution from MVP to a more production-like system.

## Why this project is strong for portfolio

- It is more memorable than a typical tracker, blog, or shop.
- It has enough business logic to discuss on interviews.
- It can start small and grow for months.
- It has a realistic path for monetization.
- It lets you explain why each technology was added.

## What makes it different from a basic habit tracker

Basic habit tracker:

- create habit;
- mark done;
- see streak.

This project:

- uses game mechanics as a domain model;
- stores events and progression history;
- computes rewards and penalties through rules;
- unlocks achievements from conditions;
- supports scheduled resets and delayed actions;
- can later support seasons, leagues, inventory, and premium mechanics.

## Main product fantasy

The user is not "tracking tasks". The user is developing a character.

Examples:

- "Read 20 pages" gives intellect XP.
- "Workout" gives strength XP.
- Missing a critical quest applies a penalty.
- A 7-day streak unlocks a badge.
- Reaching level 5 unlocks a new skill node.

This framing makes the project emotionally interesting and technically rich.

## Target audience

Primary:

- students;
- self-improvement users;
- people who like productivity with game mechanics.

Secondary:

- creators who want gamified communities later;
- Telegram or mobile users if you extend the project.

## Core principles

- Backend first.
- Frontend is optional at the start.
- Every added technology must solve a real problem.
- MVP must be small enough to finish.
- Growth stages must introduce one learning layer at a time.

## MVP scope

The first version should prove the core loop:

1. User registers and logs in.
2. User creates habits and quests.
3. User marks completion.
4. System grants XP and updates streaks.
5. User sees character progress and event history.

If this loop works well, the project already becomes portfolio-worthy.

## MVP features

- user registration and authentication;
- character profile;
- habit creation;
- daily quest and one-time quest creation;
- completion endpoint;
- XP and level calculation;
- streak tracking;
- event log;
- simple statistics page via API;
- admin panel for inspection.

## Features explicitly excluded from MVP

Do not build these first:

- inventory;
- skill tree;
- guilds;
- leaderboards;
- social features;
- payments;
- Telegram bot;
- WebSocket;
- AI features.

These are expansion stages, not starting requirements.

## Suggested stack by stage

### Stage 1: MVP

- Python
- Django
- Django REST Framework
- PostgreSQL
- pytest
- Docker

### Stage 2: Better API and developer quality

- drf-spectacular for OpenAPI
- django-filter
- pre-commit
- Ruff

### Stage 3: Background processing

- Celery
- Redis

### Stage 4: Deployment and ops

- Gunicorn
- Nginx
- Docker Compose
- Sentry or basic error monitoring

### Stage 5: Optional product growth

- Telegram bot
- WebSocket
- OpenAI integration
- payment integration

## Why this stack order is correct

- Django and DRF teach structure and API basics.
- PostgreSQL teaches real database work.
- pytest teaches confidence and regression prevention.
- Docker makes the project more professional without changing logic.
- Celery and Redis only become necessary when you add scheduled jobs and background processing.

This order prevents "stack cosplay" where tools are added just to look advanced.

## Domain model for MVP

### User

Use Django's user model or a custom user model if you want clean future extensibility.

Fields:

- username
- email
- password
- created_at

### CharacterProfile

One profile per user.

Fields:

- user
- character_name
- level
- total_xp
- current_streak
- longest_streak
- created_at
- updated_at

### Habit

Represents a repeated behavior.

Fields:

- user
- title
- description
- difficulty
- xp_reward
- penalty_enabled
- is_active
- created_at

### Quest

Represents a concrete actionable objective.

Types:

- daily
- one_time

Fields:

- user
- habit
- title
- quest_type
- status
- due_date
- completed_at
- created_at

### Completion

Stores quest completion facts.

Fields:

- user
- quest
- completed_at
- awarded_xp

### Achievement

Represents unlockable badges.

Fields:

- code
- title
- description
- condition_type
- condition_value

### UserAchievement

Fields:

- user
- achievement
- unlocked_at

### EventLog

This is important for explainability and debugging.

Fields:

- user
- event_type
- payload_json
- created_at

Examples:

- quest_completed
- xp_awarded
- level_up
- streak_updated
- achievement_unlocked

## Relationships

- User -> one CharacterProfile
- User -> many Habits
- User -> many Quests
- Quest -> optional Habit
- Quest -> many Completion entries only if your model allows retries, otherwise one completion record
- User -> many EventLog entries
- User -> many achievements through UserAchievement

## MVP business rules

These rules are the heart of the backend.

### XP rule

- Each quest gives a fixed XP reward.
- Difficulty can modify XP.
- XP is granted only once per eligible completion.

### Level rule

Keep it simple first:

- level 1 starts at 0 XP;
- every 100 XP gives one new level.

Later you can switch to a nonlinear formula.

### Daily streak rule

- Completing at least one daily quest for a day maintains a streak.
- Missing a day resets the streak.
- Longest streak is preserved.

### Achievement rule

Start with 3 to 5 simple achievements:

- first quest completed;
- streak of 3 days;
- reach level 3;
- complete 10 quests;
- create 5 habits.

### Event log rule

Every important state change should create an event.

This gives you:

- easier debugging;
- explainable progression;
- future analytics source;
- good interview talking points.

## Important engineering constraints

### Idempotency

Completion endpoints must not grant XP twice by accident.

You should explicitly protect against:

- repeated client requests;
- browser refresh resubmits;
- double-clicks;
- race conditions later.

### Transactions

When a quest is completed, these updates should be treated as one unit:

- mark quest completed;
- create completion record;
- grant XP;
- update level;
- update streak if needed;
- create events;
- unlock achievements if conditions are met.

Use database transactions so partial updates do not leave broken state.

### Permissions

A user must only access their own habits, quests, profile, and events.

This is basic but important backend hygiene.

## Suggested API for MVP

### Auth

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/refresh/`

### Character

- `GET /api/profile/`
- `PATCH /api/profile/`

### Habits

- `GET /api/habits/`
- `POST /api/habits/`
- `GET /api/habits/{id}/`
- `PATCH /api/habits/{id}/`
- `DELETE /api/habits/{id}/`

### Quests

- `GET /api/quests/`
- `POST /api/quests/`
- `GET /api/quests/{id}/`
- `PATCH /api/quests/{id}/`
- `DELETE /api/quests/{id}/`

### Completion

- `POST /api/quests/{id}/complete/`

This endpoint should trigger core business logic.

### Achievements

- `GET /api/achievements/`

### Event log

- `GET /api/events/`

### Stats

- `GET /api/stats/`

Response can include:

- level
- total_xp
- current_streak
- longest_streak
- completed_quests_count
- achievements_count

## Recommended project structure

```text
quest-rpg/
  manage.py
  config/
    settings/
    urls.py
  apps/
    accounts/
    characters/
    habits/
    quests/
    achievements/
    events/
    progression/
  tests/
  docker-compose.yml
  Dockerfile
  pyproject.toml
  README.md
```

## App responsibility split

### accounts

- authentication;
- user creation;
- user-related serializers.

### characters

- profile model;
- level and XP read models;
- profile endpoints.

### habits

- habit CRUD.

### quests

- quest CRUD;
- completion endpoint entry.

### achievements

- achievement definitions;
- unlocking records.

### events

- event log storage;
- audit-style history endpoints.

### progression

- pure business services:
  - grant_xp;
  - update_level;
  - update_streak;
  - unlock_achievements.

This split is strong for interviews because you can explain where business logic lives.

## Service-layer idea

Do not bury all logic in serializers or views.

Use application services such as:

- `complete_quest(user, quest_id)`
- `grant_xp(profile, amount)`
- `check_achievements(user)`

Benefits:

- better testing;
- thinner API layer;
- easier future growth;
- cleaner explanation during interviews.

## Test strategy

For a junior portfolio, tests are a major advantage.

Minimum test groups:

- auth tests;
- permissions tests;
- quest completion tests;
- XP and level tests;
- streak tests;
- achievement unlock tests;
- duplicate completion protection tests.

Critical point:

You do not need huge coverage. You need good coverage of the risky logic.

## Development roadmap

### Milestone 0: Foundation

- create repository;
- configure Django, DRF, PostgreSQL;
- add Docker;
- set up linting and test runner;
- create README with project idea.

Deliverable:

- empty but professional project skeleton.

### Milestone 1: Auth and character

- registration/login;
- create character profile automatically;
- profile endpoint.

Deliverable:

- user can create account and inspect profile.

### Milestone 2: Habits and quests

- habit CRUD;
- quest CRUD;
- connect quest to habit.

Deliverable:

- user can create the gameplay structure.

### Milestone 3: Completion engine

- complete quest endpoint;
- XP awarding;
- level updates;
- event log creation;
- transaction handling.

Deliverable:

- first real game loop.

### Milestone 4: Streaks and achievements

- streak calculation;
- basic achievements;
- achievements endpoint;
- more tests.

Deliverable:

- progression becomes emotionally rewarding.

### Milestone 5: API quality and docs

- filters;
- pagination;
- OpenAPI docs;
- better README;
- curl examples.

Deliverable:

- project becomes interview-ready.

### Milestone 6: Background jobs

- Celery and Redis;
- scheduled daily checks;
- reset or maintenance jobs;
- delayed achievement or reminder tasks.

Deliverable:

- you can explain async and background processing with a real use case.

### Milestone 7: Product expansion

Choose one, not all:

- inventory system;
- skill tree;
- Telegram integration;
- seasonal challenges;
- league and leaderboard.

Deliverable:

- project becomes differentiated.

## Best first expansion after MVP

Pick exactly one of these:

1. Achievement engine
2. Inventory and rewards
3. Daily scheduler with Celery
4. Telegram bot interface

Recommended first expansion:

- Achievement engine

Reason:

- very visible;
- lots of backend logic;
- low infrastructure cost.

## Monetization paths

- premium themes or advanced progression systems;
- paid community challenges;
- paid analytics;
- Telegram premium bot features;
- white-label gamification engine for creators;
- team mode for small groups.

Do not build monetization first. Just keep the domain open for it.

## What to say in interviews

Good framing:

- "I intentionally chose a backend-heavy project with a nontrivial domain model."
- "I separated API concerns from progression logic."
- "I used transactions to keep completion, XP, streak, and achievement updates consistent."
- "I added event logging so state changes are explainable and testable."
- "I introduced Celery only when scheduled jobs became necessary."

This sounds much stronger than "I built a CRUD app".

## Common mistakes to avoid

- Making the MVP too large.
- Adding frontend too early.
- Adding Celery before you need scheduled work.
- Putting all logic into views or serializers.
- Building social features before the single-user loop is solid.
- Using too many game mechanics before the core progression feels good.

## Definition of success for version 1

Version 1 is successful if:

- a user can register;
- create habits and quests;
- complete a quest;
- gain XP and levels;
- maintain streaks;
- unlock at least a few achievements;
- inspect progress through API responses;
- the core logic is covered by tests.

That is already a strong junior portfolio project.

## Practical next step

Start with Milestone 0 and Milestone 1 only.

Do not design the whole universe in code on day one.

Build:

- repository structure;
- Django project;
- auth;
- character profile.

Then stop and verify the base before moving to habits and quests.

## If you build this with Codex

Use Codex as:

- scaffolding assistant;
- reviewer of architecture choices;
- explainer of Django internals;
- test writer helper;
- refactor assistant.

Do not use it only as a "make everything for me" button.

For each milestone, ask:

- what problem this code solves;
- why this model is shaped this way;
- why this endpoint belongs here;
- what could break;
- how this should be tested.

That is how the project becomes both portfolio and training.
