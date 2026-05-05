# ⚙️ Archivos de configuración listos para usar

## 1. docker-compose.yml (MVP)

Copia este archivo a la raíz del proyecto:

```yaml
version: '3.8'

services:
  # PostgreSQL 15
  postgres:
    image: postgres:15-alpine
    container_name: acustica_postgres
    environment:
      POSTGRES_USER: acustica
      POSTGRES_PASSWORD: dev_password_change_me
      POSTGRES_DB: acustica_db
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=C"
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "acustica"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
    networks:
      - acustica-network
    restart: unless-stopped

  # FastAPI Backend
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: acustica_backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://acustica:dev_password_change_me@postgres:5432/acustica_db
      ENVIRONMENT: development
      DEBUG: "true"
      PYTHONUNBUFFERED: "1"
    volumes:
      - ./backend:/app
      - /app/__pycache__  # Evita sincronizar cache
    depends_on:
      postgres:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    networks:
      - acustica-network
    restart: unless-stopped

  # Next.js Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: acustica_frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://backend:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules      # Evita sincronizar node_modules
      - /app/.next              # Caché de Next.js
    depends_on:
      - backend
    command: npm run dev
    networks:
      - acustica-network
    restart: unless-stopped

volumes:
  postgres_data:
    driver: local

networks:
  acustica-network:
    driver: bridge
```

**Cómo usar:**
```bash
# Inicia todos los servicios
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f

# Detener
docker-compose down

# Detener + eliminar volúmenes (cuidado: pierde BD)
docker-compose down -v
```

---

## 2. backend/requirements.txt

```txt
# FastAPI & web server
fastapi==0.115.0
uvicorn[standard]==0.30.0

# Database
sqlalchemy==2.1.0
psycopg2-binary==2.9.10
alembic==1.14.0

# Validation & serialization
pydantic==2.8.0
pydantic-settings==2.4.0
python-multipart==0.0.6

# Cálculos científicos
numpy==1.26.0
scipy==1.14.0

# Testing
pytest==8.2.0
pytest-asyncio==0.24.0
pytest-cov==5.0.0
httpx==0.27.0

# Utilities
python-dotenv==1.0.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Security
cors==1.0.1

# Logging & monitoring (opcional pero recomendado)
python-json-logger==2.0.7
sentry-sdk==1.45.0

# Code quality
black==24.3.0
flake8==7.1.1
isort==5.13.2
mypy==1.11.0
```

**Instalación:**
```bash
pip install -r backend/requirements.txt
```

---

## 3. backend/Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Instala herramientas del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements y instala dependencias
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copia código de la aplicación
COPY . .

# Expone puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Comando por defecto
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 4. frontend/package.json

```json
{
  "name": "acustica-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint && prettier --check .",
    "format": "prettier --write .",
    "test": "jest",
    "test:watch": "jest --watch"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "next": "^15.0.0",
    "typescript": "^5.4.5",
    "tailwindcss": "^3.4.3",
    "postcss": "^8.4.38",
    "autoprefixer": "^10.4.19",
    "plotly.js": "^2.28.0",
    "react-plotly.js": "^2.0.0",
    "axios": "^1.7.2",
    "zustand": "^4.4.7"
  },
  "devDependencies": {
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "@types/node": "^20.12.12",
    "eslint": "^8.57.0",
    "eslint-config-next": "^15.0.0",
    "prettier": "^3.3.3",
    "jest": "^29.7.0",
    "@testing-library/react": "^14.2.1",
    "@testing-library/jest-dom": "^6.1.5"
  }
}
```

---

## 5. frontend/Dockerfile

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Variables de entorno
ENV NEXT_TELEMETRY_DISABLED=1

# Copia package files
COPY package*.json ./

# Instala dependencias
RUN npm ci

# Copia código
COPY . .

# Build (desarrollo sin build)
# En desarrollo, ejecutamos: npm run dev
# En producción: npm run build && npm start

EXPOSE 3000

CMD ["npm", "run", "dev"]
```

---

## 6. .devcontainer/devcontainer.json

```json
{
  "name": "Acustica Platform Dev",
  "image": "mcr.microsoft.com/devcontainers/base:ubuntu-22.04",
  
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {
      "version": "latest"
    },
    "ghcr.io/devcontainers/features/node:18": {},
    "ghcr.io/devcontainers/features/python:3.11": {
      "version": "3.11"
    },
    "ghcr.io/devcontainers/features/git:latest": {}
  },
  
  "forwardPorts": [3000, 8000, 5432],
  "portsAttributes": {
    "3000": {
      "label": "Frontend (Next.js)",
      "onAutoForward": "notify"
    },
    "8000": {
      "label": "Backend (FastAPI)",
      "onAutoForward": "notify"
    },
    "5432": {
      "label": "PostgreSQL",
      "onAutoForward": "silent"
    }
  },
  
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-python.debugpy",
        "ms-python.flake8",
        "ms-python.black-formatter",
        "ms-vscode.makefile-tools",
        "esbenp.prettier-vscode",
        "dbaeumer.vscode-eslint",
        "bradlc.vscode-tailwindcss",
        "GitHub.copilot",
        "ms-vscode-remote.remote-containers",
        "ms-azuretools.vscode-docker"
      ],
      "settings": {
        "python.linting.enabled": true,
        "python.linting.flake8Enabled": true,
        "python.formatting.provider": "black",
        "python.testing.pytestEnabled": true,
        "editor.defaultFormatter": "esbenp.prettier-vscode",
        "editor.formatOnSave": true,
        "[python]": {
          "editor.defaultFormatter": "ms-python.black-formatter",
          "editor.formatOnSave": true
        }
      }
    }
  },
  
  "postCreateCommand": "bash .devcontainer/post-create.sh",
  "postStartCommand": "docker-compose ps && echo '✅ Codespace ready!'",
  
  "remoteUser": "root",
  "mounts": [
    "source=${localEnv:HOME}/.ssh,target=/root/.ssh,type=bind,consistency=cached"
  ]
}
```

---

## 7. .devcontainer/post-create.sh

```bash
#!/bin/bash
set -e

echo "🚀 Configurando entorno de desarrollo..."

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Cambiar a directorio del proyecto
cd /workspaces/$(ls /workspaces)

echo -e "${BLUE}📦 Instalando dependencias de Python...${NC}"
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r backend/requirements.txt

echo -e "${BLUE}📦 Instalando dependencias de Node.js...${NC}"
cd frontend
npm install
cd ..

echo -e "${BLUE}🐳 Iniciando servicios Docker...${NC}"
docker-compose up -d

# Esperar a que PostgreSQL esté listo
echo -e "${YELLOW}⏳ Esperando PostgreSQL...${NC}"
max_attempts=30
attempt=1
while [ $attempt -le $max_attempts ]; do
  if docker-compose exec -T postgres pg_isready -U acustica > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL está listo${NC}"
    break
  fi
  echo "  Intento $attempt/$max_attempts..."
  sleep 2
  attempt=$((attempt + 1))
done

if [ $attempt -gt $max_attempts ]; then
  echo -e "${YELLOW}⚠️ PostgreSQL tardó más de lo esperado. Continuando...${NC}"
fi

# Ejecutar migraciones
echo -e "${BLUE}🔄 Ejecutando migraciones de BD...${NC}"
cd backend
alembic upgrade head || echo "⚠️ Migraciones pueden no existir aún (normal en primer setup)"
cd ..

# Verificar que todo está UP
echo -e "${BLUE}🔍 Verificando servicios...${NC}"
docker-compose ps

echo -e "${GREEN}✅ Entorno listo!${NC}"
echo ""
echo -e "${BLUE}Próximos pasos:${NC}"
echo "1. Abre http://localhost:3000 en tu navegador (Frontend)"
echo "2. Abre http://localhost:8000/docs para Swagger (Backend)"
echo "3. Para ver logs: docker-compose logs -f"
echo ""
echo -e "${YELLOW}Para detener: docker-compose down${NC}"
```

**Dale permisos ejecutables:**
```bash
chmod +x .devcontainer/post-create.sh
```

---

## 8. backend/.env.example

```env
# Database
DATABASE_URL=postgresql://acustica:dev_password_change_me@localhost:5432/acustica_db

# API
API_TITLE=Plataforma Acustica
API_VERSION=0.1.0
DEBUG=true
ENVIRONMENT=development

# Security (cambiar en producción)
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Logging
LOG_LEVEL=INFO
```

**Uso:**
```bash
cp backend/.env.example backend/.env
# Edita backend/.env con tus valores
```

---

## 9. .github/workflows/ci.yml

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  # Tests del Backend
  test-backend:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: acustica
          POSTGRES_PASSWORD: dev_password_change_me
          POSTGRES_DB: acustica_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: pip install -r backend/requirements.txt
      
      - name: Lint with flake8
        run: |
          flake8 backend/app backend/engine --max-line-length=100 --exclude=migrations
        continue-on-error: true
      
      - name: Check formatting with black
        run: black --check backend/app backend/engine
        continue-on-error: true
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://acustica:dev_password_change_me@localhost:5432/acustica_db
        run: |
          pytest backend/tests --cov=backend.app --cov=backend.engine --cov-report=xml -v
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: backend
        continue-on-error: true

  # Tests del Frontend
  test-frontend:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        run: cd frontend && npm ci
      
      - name: Lint
        run: cd frontend && npm run lint
        continue-on-error: true
      
      - name: Build
        run: cd frontend && npm run build
      
      - name: Run tests
        run: cd frontend && npm run test -- --coverage
        continue-on-error: true

  # Build Docker (solo en main)
  build-docker:
    needs: [test-backend, test-frontend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Build backend
        uses: docker/build-push-action@v4
        with:
          context: ./backend
          push: false
          tags: acustica-backend:latest
      
      - name: Build frontend
        uses: docker/build-push-action@v4
        with:
          context: ./frontend
          push: false
          tags: acustica-frontend:latest
```

---

## 10. .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
.venv/
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.mypy_cache/
.dmypy.json
dmypy.json

# Node
node_modules/
npm-debug.log
yarn-error.log
.next/
out/
dist/

# Environment files
.env
.env.local
.env.*.local

# Docker
.docker/
postgres_data/

# Temporal
*.tmp
*.bak
*.swp

# Archivos generados
.cache/
.pytest_cache/

# Mac
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite
*.sqlite3
```

---

## 11. tsconfig.json (Frontend)

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
```

---

## 12. next.config.js

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },

  // API proxy en desarrollo (para CORS)
  async rewrites() {
    if (process.env.NODE_ENV === 'development') {
      return {
        beforeFiles: [
          {
            source: '/api/:path*',
            destination: 'http://backend:8000/api/:path*',
          },
        ],
      };
    }
    return {};
  },

  // CORS headers
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Access-Control-Allow-Credentials',
            value: 'true',
          },
          {
            key: 'Access-Control-Allow-Origin',
            value: '*',
          },
          {
            key: 'Access-Control-Allow-Methods',
            value: 'GET,OPTIONS,PATCH,DELETE,POST,PUT',
          },
          {
            key: 'Access-Control-Allow-Headers',
            value: 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
```

---

## 13. tailwind.config.js

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',    // Azul
        secondary: '#10B981',  // Verde
        accent: '#F59E0B',     // Ámbar
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
};
```

---

## 14. pytest.ini

```ini
[pytest]
testpaths = backend/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --color=yes

markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
    api: API endpoint tests

log_cli = true
log_cli_level = INFO
log_cli_format = %(asctime)s [%(levelname)8s] %(message)s
log_cli_date_format = %Y-%m-%d %H:%M:%S
```

---

## 🚀 Quick Start Command

```bash
# 1. Clone el repo (asume que ya lo tienen)
cd proyecto-acustica

# 2. Copia archivos de configuración
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 3. Inicia Docker
docker-compose up -d

# 4. Espera a que levante (20-30 segundos)
sleep 30

# 5. Verifica
docker-compose ps
curl http://localhost:8000/health
curl http://localhost:3000

# 6. Abre en navegador
# Frontend: http://localhost:3000
# Backend Docs: http://localhost:8000/docs
# Postgres: localhost:5432 (en cliente psql)
```

---

**Última actualización:** Mayo 2026
