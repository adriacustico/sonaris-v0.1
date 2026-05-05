# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Sonaris** is a SaaS web platform for acoustic calculations. The codebase is primarily documented and written in Spanish.

- **Backend**: FastAPI (Python 3.11) on port 8000
- **Frontend**: Next.js 15 + TypeScript + React 18 on port 3000
- **Database**: PostgreSQL 15 on port 5432

## Commands

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload        # dev server
pytest                                # all tests
pytest engine/tests/                  # engine tests only
pytest engine/tests/test_foo.py::test_bar  # single test
pytest -m unit                        # by marker (unit, integration, slow)
```

### Frontend
```bash
cd frontend
npm install
npm run dev        # dev server
npm run build
npm run lint
npm run typecheck
```

### Docker (full stack)
```bash
docker-compose up -d     # start all services
docker-compose logs -f
docker-compose down
```

Copy `.env.example` to `.env` before running locally without Docker.

## Architecture

### Backend layers

```
backend/app/          FastAPI application
  api/                Route handlers (auth, projects, calculations)
  core/               Config (pydantic-settings) and security
  db/                 SQLAlchemy session factory and DeclarativeBase
  models/             ORM models: User, Project, Calculation
  schemas/            Pydantic request/response schemas
  main.py             App factory, middleware, router registration

backend/engine/       Acoustic calculation engine — intentionally independent of FastAPI
  acoustic_engine.py  Facade class (entry point for all calculations)
  calculations/       Formula implementations: ISO 717-1, SHARP
  materials.py        Material database (density, acoustic properties)
  tests/              pytest tests for the engine
```

The engine layer must stay decoupled from FastAPI so it can be tested and used independently. All new acoustic formulas go in `backend/engine/calculations/`.

### Frontend structure

```
frontend/app/         Next.js App Router
  (dashboard)/        Dashboard route group
  projects/           Projects pages
  api/                Internal API routes (e.g., health check)
frontend/components/
  Calculator/         Main acoustic calculator UI
  ui/                 Shared UI primitives
frontend/lib/api.ts   Typed fetch wrapper — all backend calls go through here
```

Custom Tailwind colors: `ink` (#172026), `signal` (#0f766e), `surface` (#f6f8f9).

### API surface

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/auth/login` | Auth (placeholder) |
| GET/POST | `/projects/` | Project CRUD |
| POST | `/calculations/` | Run a calculation |

### Database models

- `User` — email + hashed password + active flag
- `Project` — acoustic project owned by a user
- `Calculation` — result record with input/output stored as JSON columns

Alembic is configured for migrations (not yet actively used).

## Development notes

- The acoustic formulas in `engine/calculations/` currently return placeholder values (fixed 20 dB). Implementing real ISO 717-1 / SHARP logic is ongoing work.
- CORS is configured for `http://localhost:3000` only.
- CI (`.github/workflows/ci.yml`) runs `pytest` for the backend and `npm run typecheck` for the frontend on every push to `main` and all PRs.
