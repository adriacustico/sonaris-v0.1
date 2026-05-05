# 🎯 Guía: Claude Code en VS Code para Proyecto de Cálculos Acústicos

**Proyecto:** Plataforma web SaaS de cálculos acústicos  
**Stack:** FastAPI + Next.js + PostgreSQL + Docker + Codespaces  
**Objetivo:** Desarrollo remoto sin fricción usando Claude Code como co-pilot de IA

---

## 📋 Tabla de contenidos

1. [Requisitos previos](#requisitos-previos)
2. [Instalación de Claude Code](#instalación-de-claude-code)
3. [Setup inicial del proyecto](#setup-inicial-del-proyecto)
4. [Flujo de trabajo con Claude Code](#flujo-de-trabajo-con-claude-code)
5. [Estrategia por capas (Backend → Motor → Frontend)](#estrategia-por-capas)
6. [Desarrollo remoto en Codespaces](#desarrollo-remoto-en-codespaces)
7. [Prompts efectivos para Claude Code](#prompts-efectivos-para-claude-code)
8. [Troubleshooting y mejores prácticas](#troubleshooting-y-mejores-prácticas)

---

## Requisitos previos

### En tu máquina local (o Codespace)

- **VS Code** (v1.95+)
- **Docker** y **Docker Compose**
- **Git**
- **Node.js 18+** (para Claude Code)
- **Python 3.11+** (para desarrollo local sin Docker)

### Acceso a Claude Code

> 📍 **Fuente oficial:** https://docs.anthropic.com/en/docs/claude-code/overview

- Claude Code es un **feature de Claude** que permite escribir, ejecutar y iterar sobre código directamente
- Disponible en **Claude.ai Pro** o superior
- También integrable en tu propio entorno VS Code mediante la extensión oficial

---

## Instalación de Claude Code

### Opción 1: Usar Claude Code desde la web (claude.ai)

**Ventaja:** Cero instalación  
**Desventaja:** No está integrado directamente en tu VS Code local

1. Ve a [claude.ai](https://claude.ai)
2. Abre un nuevo chat
3. Menciona "write code" o sube archivos de tu proyecto
4. Claude ejecutará código en el sandbox integrado

### Opción 2: Extensión de Claude Code para VS Code (Recomendado para este proyecto)

📍 **npm package:** https://www.npmjs.com/package/@anthropic-ai/claude-code

#### Pasos:

```bash
# 1. Instala la extensión en VS Code
# Abre VS Code → Extensions (Ctrl+Shift+X) 
# Busca: "Claude Code" por Anthropic
# Haz clic en "Install"

# 2. Configura tu API key
# - Obtén tu clave en: https://console.anthropic.com
# - En VS Code: Ctrl+Shift+P → "Preferences: Open Settings (JSON)"
# - Agrega:
{
  "claude-code.apiKey": "tu-clave-aqui"
}

# 3. Verifica la instalación
code --version  # VS Code
node --version  # Node.js 18+
docker --version  # Docker
```

---

## Setup inicial del proyecto

### Estructura de carpetas recomendada

```
proyecto-acustica/
├── .devcontainer/
│   ├── devcontainer.json        ← Configuración para Codespaces
│   └── Dockerfile               ← Imagen del contenedor
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              ← FastAPI app
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── projects.py       ← Endpoints de proyectos
│   │   │   ├── calculations.py   ← Endpoints de cálculos
│   │   │   └── auth.py           ← Endpoints de autenticación
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   └── calculation.py
│   │   ├── schemas/
│   │   │   └── *.py              ← Pydantic models
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── session.py        ← SQLAlchemy session
│   │   │   └── alembic/          ← Migraciones
│   │   └── core/
│   │       ├── config.py
│   │       └── security.py
│   ├── engine/                   ← MOTOR DE CÁLCULO (núcleo)
│   │   ├── __init__.py
│   │   ├── acoustic_engine.py    ← Clase principal
│   │   ├── materials.py          ← Librería de materiales
│   │   ├── calculations/
│   │   │   ├── iso12354_1.py     ← Cálculo ISO 12354-1
│   │   │   ├── iso717_1.py       ← Ponderación ISO 717-1
│   │   │   └── utils.py
│   │   └── tests/
│   │       ├── test_iso12354.py
│   │       ├── test_materials.py
│   │       └── fixtures.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── pytest.ini
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── (projects)/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   └── [id]/
│   │   │       ├── page.tsx
│   │   │       └── edit.tsx
│   │   └── api/
│   │       └── [...].ts          ← API routes locales
│   ├── components/
│   │   ├── Header.tsx
│   │   ├── ProjectCard.tsx
│   │   ├── Calculator.tsx        ← Interfaz principal
│   │   └── Charts/
│   ├── lib/
│   │   └── api-client.ts         ← Cliente HTTP
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   └── Dockerfile
├── docker-compose.yml
├── .github/
│   └── workflows/
│       └── ci.yml                ← GitHub Actions
├── .gitignore
├── README.md
└── DEVELOPMENT.md                ← Guía de desarrollo (generada por Claude Code)
```

### Archivo: `docker-compose.yml` (MVP)

```yaml
version: '3.8'

services:
  # Base de datos
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: acustica
      POSTGRES_PASSWORD: dev_password_change_me
      POSTGRES_DB: acustica_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "acustica"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Backend FastAPI
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://acustica:dev_password_change_me@postgres:5432/acustica_db
      ENVIRONMENT: development
      DEBUG: "true"
    volumes:
      - ./backend:/app
    depends_on:
      postgres:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # Frontend Next.js
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
    command: npm run dev

volumes:
  postgres_data:

networks:
  default:
    name: acustica-network
```

### Archivo: `.devcontainer/devcontainer.json` (para Codespaces)

```json
{
  "name": "Acustica Platform",
  "image": "mcr.microsoft.com/devcontainers/base:ubuntu-22.04",
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {},
    "ghcr.io/devcontainers/features/node:18": {},
    "ghcr.io/devcontainers/features/python:3.11": {}
  },
  "forwardPorts": [3000, 8000, 5432],
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-python.debugpy",
        "ms-python.flake8",
        "esbenp.prettier-vscode",
        "dbaeumer.vscode-eslint",
        "bradlc.vscode-tailwindcss",
        "ms-vscode.makefile-tools",
        "GitHub.copilot"
      ]
    }
  },
  "postCreateCommand": "bash .devcontainer/post-create.sh",
  "remoteUser": "root"
}
```

### Archivo: `.devcontainer/post-create.sh`

```bash
#!/bin/bash
set -e

echo "🚀 Configurando entorno de Codespaces..."

# Instala dependencias del proyecto
cd /workspaces/proyecto-acustica

# Backend
echo "📦 Instalando dependencias de Python..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# Frontend
echo "📦 Instalando dependencias de Node.js..."
cd frontend
npm install
cd ..

# Inicia Docker Compose
echo "🐳 Iniciando servicios Docker..."
docker-compose up -d

# Espera a que PostgreSQL esté listo
echo "⏳ Esperando PostgreSQL..."
until docker exec proyecto-acustica-postgres-1 pg_isready -U acustica > /dev/null 2>&1; do
  sleep 2
done

# Migraciones de BD
echo "🔄 Ejecutando migraciones..."
cd backend
alembic upgrade head
cd ..

echo "✅ Entorno listo. Ejecuta: docker-compose logs -f"
```

---

## Flujo de trabajo con Claude Code

### 📌 Estructura mental: 3 fases

```
FASE 1: Planificación
  └─ Claude Code genera la arquitectura exacta
  
FASE 2: Scaffolding (generación de estructura)
  └─ Claude Code crea todos los archivos base
  
FASE 3: Implementación iterativa
  └─ Desarrollas con Claude Code como navegador + codificador
```

---

### FASE 1: Planificación y Scaffolding

#### Prompt de inicio (copia y pega en Claude Code)

```
Te necesito para ayudarme a crear una plataforma web de cálculos acústicos.

Contexto:
- Stack: FastAPI (backend) + Next.js (frontend) + PostgreSQL
- Desarrollo en Docker + Codespaces
- MVP sin workers (Celery) ni Redis inicialmente

Necesito que:

1) **Generes la estructura completa de carpetas** 
   - Backend modular con separación clara: API ≠ motor de cálculo
   - Frontend Next.js con estructura para proyectos y cálculos
   - Dockerfiles para ambos servicios
   - docker-compose.yml para orquestar: postgres, backend, frontend

2) **Crees los archivos base iniciales** (vacíos pero con placeholders documentados):
   - backend/app/main.py (FastAPI app con rutas base)
   - backend/engine/acoustic_engine.py (clase AcousticEngine)
   - backend/models/*.py (SQLAlchemy models: User, Project, Calculation)
   - frontend/app/page.tsx (página de bienvenida)
   - requirements.txt con dependencias: FastAPI, SQLAlchemy, Pydantic, NumPy, SciPy

3) **Me des una hoja de ruta clara** 
   - Qué construir primero
   - Dependencias entre módulos
   - Cómo testear cada pieza

Empezamos ahora.
```

#### Qué esperar

Claude Code debería:

✅ **Crear todos los archivos** con un solo comando  
✅ **Documentar cada módulo** con comentarios claros  
✅ **Mostrar cómo ejecutar** `docker-compose up` para iniciar todo  
✅ **Indicarte qué hacer después** de manera clara

---

### FASE 2: Scaffolding del motor de cálculo

Una vez que tengas la estructura base:

#### Prompt para el motor de cálculo

```
Ahora vamos con el núcleo del negocio: el motor de cálculos acústicos.

Necesito:

1) **Clase base AcousticEngine** (en backend/engine/acoustic_engine.py)
   - Constructor que reciba un diccionario de configuración
   - Método calcular_aislamiento(materiales, frecuencias) → devuelve R(f)
   - Método aplicar_iso717_1(R_frecuencias) → devuelve Rw, C, Ctr
   - Manejo de errores con excepciones personalizadas

2) **Módulo de materiales** (backend/engine/materials.py)
   - Clase Material con propiedades: nombre, densidad, espesor, factor_pérdida
   - Base de datos en memoria (dict) con ~50 materiales comunes
   - Método para buscar material por nombre
   - Método para interpolar propiedades si no existen

3) **Cálculos ISO 12354-1 y ISO 717-1** (backend/engine/calculations/)
   - iso12354_1.py: fórmulas de Sharp/Davy para R(f)
   - iso717_1.py: ponderación con curva de referencia
   - Tests unitarios para cada función

4) **Patrón de importación**
   - El backend puede hacer: from engine.acoustic_engine import AcousticEngine
   - Sin necesidad de conocer los detalles internos

Generamelo todo con tests incluidos.
```

---

### FASE 3: Endpoints FastAPI

```
Ahora expongo el motor en FastAPI.

Crea estos endpoints en backend/app/api/calculations.py:

1) POST /api/calculations/simple
   - Input: { materiales: [], frecuencias: [] }
   - Output: { R_por_frecuencia: {}, Rw: 45, C: -3, Ctr: -8 }
   - Usa AcousticEngine internamente

2) POST /api/calculations/guardar
   - Input: { proyecto_id, nombre, datos_entrada, resultado }
   - Guarda en BD (tabla Calculation)
   - Output: { id, creado_en, resultado }

3) GET /api/calculations/{id}
   - Devuelve un cálculo guardado con toda la traza

4) GET /api/materiales
   - Devuelve lista de materiales disponibles
   - Query params: ?search=hormigon

Generamelo e integramelo al docker-compose para que funcione desde el primer `docker-compose up`.
```

---

## Estrategia por capas

### 🎯 La clave: Separación motor ≠ API

```
┌─────────────────────────────────────────┐
│         FRONTEND (Next.js)              │
│  - Formularios                          │
│  - Gráficos (Plotly/Chart.js)           │
│  - Gestión de proyectos (UI)            │
└──────────────┬──────────────────────────┘
               │ HTTP REST
               ↓
┌──────────────────────────────────────────┐
│      API LAYER (FastAPI)                │
│  - Autenticación                        │
│  - Validación (Pydantic)                │
│  - Persistencia (SQLAlchemy)            │
│  - Orquestación                         │
└──────────────┬──────────────────────────┘
               │ Importa
               ↓
┌──────────────────────────────────────────┐
│    MOTOR DE CÁLCULO (Python puro)       │
│  - NumPy / SciPy                        │
│  - Lógica matemática ISO 12354-1        │
│  - Totalmente agnóstico a web           │
└──────────────────────────────────────────┘
```

### Ventajas

| Aspecto | Beneficio |
|---------|-----------|
| **Testing** | Testeas el motor sin necesidad de API/BD |
| **Reutilización** | El motor puede usarse en CLI, scripts, otros servicios |
| **Escalabilidad** | Fácil mover motor a un worker (Celery) después |
| **Debugging** | Cuando hay error, sabes exactamente dónde: motor o API |

### Ejemplo: Estructura de una función de cálculo

```python
# ❌ MAL: Lógica en el endpoint
@app.post("/api/calculations")
def calculate(req: CalculationRequest):
    # Mezcla de validación, cálculo, BD, etc.
    resultado = []
    for f in req.frecuencias:
        r = req.densidad * f * req.espesor  # 🚫 Lógica aquí
    db.save(resultado)
    return resultado

# ✅ BIEN: Separación clara
# backend/engine/acoustic_engine.py
class AcousticEngine:
    def calcular(self, materiales, frecuencias):
        # Solo lógica de cálculo
        resultado = []
        for f in frecuencias:
            r = self._aplicar_formula_sharp(materiales, f)
            resultado.append(r)
        return resultado

# backend/app/api/calculations.py
from engine.acoustic_engine import AcousticEngine

engine = AcousticEngine()

@app.post("/api/calculations")
def calculate(req: CalculationRequest, db: Session):
    # Orquestación
    resultado_calc = engine.calcular(req.materiales, req.frecuencias)
    
    # Persistencia
    calc_obj = Calculation(
        proyecto_id=req.proyecto_id,
        entrada=req.dict(),
        salida=resultado_calc
    )
    db.add(calc_obj)
    db.commit()
    
    return {"id": calc_obj.id, "resultado": resultado_calc}
```

---

## Desarrollo remoto en Codespaces

### ¿Por qué Codespaces?

✅ **Entorno idéntico** a producción (Docker garantiza reproducibilidad)  
✅ **Sin instalar nada** en tu máquina  
✅ **Acceso desde cualquier navegador**  
✅ **Integración con GitHub** (mismo repo = mismo código)

### Pasos para iniciar

1. **Ve a tu repo en GitHub**
   - Click verde: "Code" → "Codespaces" → "Create codespace on main"

2. **VS Code se abre en el navegador**
   - Espera a que termine la setup (ve logs en terminal)
   - Se ejecutará automáticamente `.devcontainer/post-create.sh`

3. **Verifica que los servicios estén UP**
   ```bash
   docker-compose ps
   # postgres    ✓ healthy
   # backend     ✓ running
   # frontend    ✓ running
   ```

4. **Accede a tu app**
   - Frontend: `https://xxxx-3000.preview.app.github.dev` (link de Codespaces)
   - Backend: `https://xxxx-8000.preview.app.github.dev/docs` (Swagger)

5. **Usa Claude Code como siempre**
   - Las extensiones (Python, Prettier, ESLint) ya están instaladas
   - Mismo flujo de prompts que en local

### Sincronización con local

Si trabajas en **local + Codespaces** alternativamente:

```bash
# En local
git pull origin main      # Trae cambios de Codespaces
docker-compose up -d      # Inicia todo localmente

# En Codespaces
git push origin mi-rama   # Sube cambios
# Los ves en tu máquina con git pull
```

---

## Prompts efectivos para Claude Code

### 1️⃣ Generación de scaffolding

```
Crea la estructura completa del proyecto con todas las carpetas 
y archivos base (vacíos pero documentados).
Incluye:
- docker-compose.yml
- Dockerfiles para backend y frontend
- requirements.txt de Python
- package.json de Node.js
- .devcontainer para Codespaces
```

**Resultado:** ~30-40 archivos creados en segundos

---

### 2️⃣ Implementación de un módulo

```
Implementa el módulo de cálculos ISO 12354-1.

Requisitos:
- Toma como entrada: lista de materiales (nombre, espesor)
- Devuelve: R(f) para 1/3 octava (100-5000 Hz)
- Usa la fórmula de Sharp para materiales porosos
- Incluye validación de entrada (Pydantic)
- Tests unitarios con pytest

Usa NumPy/SciPy si necesitas.
```

**Resultado:** Archivo completo con validación, lógica y tests

---

### 3️⃣ Integración API

```
Crea un endpoint FastAPI POST /api/calculations que:
1. Reciba un JSON con { proyecto_id, materiales, frecuencias }
2. Valide con Pydantic (crear schema CalculationRequest)
3. Llame a AcousticEngine.calcular()
4. Guarde el resultado en BD (tabla Calculation, ya creada)
5. Devuelva { id, resultado, timestamp }

Incluye manejo de errores (validación, motor, BD).
```

**Resultado:** Endpoint funcional, listo para testear

---

### 4️⃣ Tests unitarios

```
Genera tests para el módulo acoustic_engine.py usando pytest.

Cubre:
- Constructor con parámetros válidos e inválidos
- Cálculo simple (un material, una frecuencia)
- Cálculo complejo (múltiples capas)
- Casos límite (espesor 0, material inválido)
- Ponderación ISO 717-1

Usa fixtures para reutilizar datos.
```

**Resultado:** Suite de tests completa, ejecutable con `pytest`

---

### 5️⃣ Frontend (componente calculadora)

```
Crea un componente React (Typescript) para la calculadora acústica.

Debe:
1. Formulario para seleccionar materiales (dropdown)
2. Inputs para cantidad/espesor de cada uno
3. Botón "Calcular"
4. Gráfico de R(f) con Plotly (eje X: frecuencia, eje Y: R dB)
5. Card con resultados: Rw, C, Ctr

Estilos con Tailwind.
Usa fetch() para llamar al endpoint /api/calculations.
```

**Resultado:** Componente funcional, integrable inmediatamente

---

### 6️⃣ CI/CD (GitHub Actions)

```
Configura GitHub Actions para:
1. Lint de Python (flake8) + formateo (black)
2. Lint de JavaScript (ESLint) + formateo (Prettier)
3. Tests de Python (pytest)
4. Build de Docker images
5. Trigger: on push a main y PR

Los tests deben pasar antes de mergear a main.
```

**Resultado:** Archivo `.github/workflows/ci.yml` funcional

---

## Troubleshooting y mejores prácticas

### ⚠️ Problema: "Docker daemon not running"

**En Codespaces:**
```bash
# El daemon debería estar automáticamente
docker ps
# Si no funciona, reinicia Codespace
```

**En local:**
```bash
# Inicia Docker Desktop
open /Applications/Docker.app  # macOS
# O abre Docker Desktop manualmente en Windows/Linux
```

---

### ⚠️ Problema: "PostgreSQL connection refused"

**Verifica que está UP:**
```bash
docker-compose ps
# postgres debe mostrar "healthy" en STATUS
```

**Reinicia servicios:**
```bash
docker-compose down -v  # Elimina todo (datos incluidos)
docker-compose up -d    # Comienza de nuevo
```

---

### ⚠️ Problema: Claude Code se tarda mucho generando código

**Alternativas:**
1. **Divide el prompt** en tareas más pequeñas
2. **Especifica exactamente** qué archivo quieres (no "todo el módulo")
3. **Usa versión web** (claude.ai) si la extensión va lenta

---

### ✅ Mejores prácticas

#### 1. Versioná tus prompts

```markdown
# Prompts de Claude Code (proyecto acústica)

## v1: Scaffolding inicial
[Prompt aquí]

## v2: Motor de cálculo
[Prompt aquí]

## v3: Endpoints FastAPI
[Prompt aquí]
```

Así reutilizas en proyectos futuros.

---

#### 2. Testea localmente antes de Codespaces

```bash
# Local: valida que todo funciona
docker-compose up -d
curl http://localhost:8000/docs  # ¿Swagger levanta?
npm run dev  # ¿Frontend corre?

# Recién entonces: push a GitHub y abre en Codespaces
```

---

#### 3. Usa `.gitignore` adecuado

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
env/

# Node
node_modules/
.next/
dist/

# Docker
.docker/

# IDE
.vscode/
.idea/

# Env
.env
.env.local

# BD
postgres_data/
```

---

#### 4. Documenta la ruta de desarrollo

Crea `DEVELOPMENT.md` (Claude Code puede hacerlo):

```markdown
# Guía de desarrollo

## Inicio rápido
\`\`\`bash
docker-compose up -d
docker-compose exec backend alembic upgrade head
\`\`\`

## Backend
- Logs: `docker-compose logs -f backend`
- Tests: `docker-compose exec backend pytest`
- API Docs: http://localhost:8000/docs

## Frontend
- Logs: `docker-compose logs -f frontend`
- Build: `npm run build`

## Estructura
- `backend/engine/` ← Lógica pura (testeable)
- `backend/app/` ← API (FastAPI)
- `frontend/` ← UI (Next.js)
```

---

#### 5. Usa comandos auxiliares con Claude Code

Pídele que te genere scripts útiles:

```bash
# Script para resetear BD
cat > ./scripts/reset-db.sh << 'EOF'
#!/bin/bash
docker-compose down -v
docker-compose up -d postgres
sleep 5
docker-compose up -d backend
docker-compose exec backend alembic upgrade head
EOF

chmod +x ./scripts/reset-db.sh
```

Luego: `./scripts/reset-db.sh` cuando necesites empezar de nuevo.

---

## 🎬 Resumen: Workflow completo día 1

### Mañana: Setup (30 minutos)

1. Crea repo en GitHub
2. Abre Codespace (o trabaja en local)
3. **Prompt en Claude Code:**
   ```
   Crea la estructura completa del proyecto de cálculos acústicos.
   Stack: FastAPI, Next.js, PostgreSQL, Docker.
   Incluye docker-compose.yml y .devcontainer para Codespaces.
   ```
4. Espera ~2 minutos
5. `docker-compose up -d`
6. Verifica que todo levante: `docker-compose ps`

### Tarde: Motor de cálculo (1-2 horas)

1. **Prompt en Claude Code:**
   ```
   Implementa el módulo AcousticEngine.
   - Clase que reciba materiales y frecuencias
   - Método calcular() usa fórmula de Sharp
   - Método ponderacion_iso717() calcula Rw
   - Incluye tests con pytest
   ```
2. Los tests pasan localmente
3. Commit a GitHub

### Mañana siguiente: API (1-2 horas)

1. **Prompt en Claude Code:**
   ```
   Crea endpoint POST /api/calculations.
   Usa AcousticEngine, valida entrada, guarda en BD.
   ```
2. Testea con Swagger en `http://localhost:8000/docs`
3. Commit

### Semana 1: Frontend (3-4 horas)

1. **Prompt en Claude Code:**
   ```
   Componente React: formulario calculadora + gráfico + resultados.
   Llamadas HTTP a /api/calculations.
   Estilos Tailwind.
   ```
2. Conecta a Backend real
3. Demo en `http://localhost:3000`

---

## 📚 Referencias oficiales

| Tema | URL |
|------|-----|
| Claude Code Docs | https://docs.anthropic.com/en/docs/claude-code/overview |
| FastAPI Docs | https://fastapi.tiangolo.com/ |
| Next.js Docs | https://nextjs.org/docs |
| Docker Compose | https://docs.docker.com/compose/ |
| GitHub Codespaces | https://github.com/features/codespaces |

---

## 🎯 Tips finales

- **Sé específico** en tus prompts: qué archivo, qué función, qué output esperado
- **Itera rápido**: mejor 10 prompts pequeños que 1 mega-prompt
- **Testea siempre**: después de que Claude Code genera código, ejecuta tests
- **Documentá mientras avanzas**: los prompts son tu documentación
- **Usa Codespaces para compartir**: comparte el link con tu equipo, todos ven el mismo entorno

---

**Última actualización:** Mayo 2026  
**Stack testado:** FastAPI 0.115+, Next.js 15+, PostgreSQL 15, Docker 26+, Node 18+
