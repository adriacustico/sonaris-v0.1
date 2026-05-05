# Sonaris

Plataforma web SaaS para calculos acusticos, con backend FastAPI, frontend Next.js y PostgreSQL.

## Inicio rapido

```bash
docker-compose up -d
```

Servicios principales:

- Frontend: http://localhost:3000
- Backend Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/health
- PostgreSQL: localhost:5432

## Estructura

- `backend/app`: API FastAPI, modelos, schemas, configuracion y sesiones de base de datos.
- `backend/engine`: motor de calculo acustico separado de la API.
- `frontend/app`: rutas de Next.js App Router.
- `.devcontainer`: configuracion para GitHub Codespaces.

## Desarrollo

```bash
docker-compose logs -f
docker-compose down
```

Los volumenes montan `backend/` y `frontend/` para hot-reload durante desarrollo.
