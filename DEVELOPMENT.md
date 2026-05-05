# Guia de desarrollo

## Requisitos

- Docker y Docker Compose
- Python 3.11 si ejecutas el backend fuera de Docker
- Node 18 si ejecutas el frontend fuera de Docker

## Backend local

```bash
pip install -r backend/requirements.txt
cd backend
uvicorn app.main:app --reload
```

## Frontend local

```bash
cd frontend
npm install
npm run dev
```

## Tests

```bash
cd backend
pytest
```

## Convenciones

- El motor de calculo debe permanecer en `backend/engine` y no depender de FastAPI.
- Los endpoints deben vivir en `backend/app/api`.
- Los modelos SQLAlchemy van en `backend/app/models`.
- Los schemas Pydantic van en `backend/app/schemas`.
