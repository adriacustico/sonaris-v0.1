#!/usr/bin/env bash
set -euo pipefail

echo "Installing backend dependencies..."
pip install -r backend/requirements.txt

echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

if command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD="docker-compose"
else
  COMPOSE_CMD="docker compose"
fi

echo "Starting Docker Compose services..."
$COMPOSE_CMD up -d

echo "Waiting for PostgreSQL..."
until $COMPOSE_CMD exec -T db pg_isready -U sonaris -d sonaris >/dev/null 2>&1; do
  sleep 2
done

echo "PostgreSQL ready"
echo "Backend running at http://localhost:8000"
echo "Frontend running at http://localhost:3000"
echo "Open Swagger UI at http://localhost:8000/docs"
