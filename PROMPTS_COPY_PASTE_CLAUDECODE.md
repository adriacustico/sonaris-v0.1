# 📖 Ejemplos y Prompts Copy-Paste para Claude Code

## Índice de prompts reutilizables

1. [Generación de scaffolding](#1-scaffolding-del-proyecto-completo)
2. [Motor de cálculo (ISO 12354-1)](#2-motor-de-cálculo-iso-12354-1)
3. [Integración con API FastAPI](#3-integración-con-api-fastapi)
4. [Tests unitarios](#4-tests-unitarios)
5. [Frontend React](#5-frontend-react)
6. [CI/CD con GitHub Actions](#6-cicd-con-github-actions)

---

## 1. Scaffolding del proyecto completo

### Prompt (copia y pega en Claude Code)

```
Necesito crear una plataforma web SaaS de cálculos acústicos.

STACK TÉCNICO:
- Backend: FastAPI + SQLAlchemy + Pydantic + Python 3.11
- Frontend: Next.js 15 + TypeScript + Tailwind CSS
- Base de datos: PostgreSQL 15
- Infraestructura: Docker + docker-compose
- Desarrollo remoto: GitHub Codespaces

REQUISITOS DE ESTRUCTURA:

1) Genera TODAS las carpetas y archivos base (sin implementación, solo placeholders):

backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    ← FastAPI app con config básica
│   ├── api/
│   │   ├── __init__.py
│   │   ├── projects.py            ← CRUD de proyectos
│   │   ├── calculations.py        ← Endpoints de cálculos
│   │   └── auth.py                ← Autenticación (basic)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                ← SQLAlchemy User model
│   │   ├── project.py             ← SQLAlchemy Project model
│   │   └── calculation.py         ← SQLAlchemy Calculation model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── project.py             ← Pydantic schemas
│   │   └── calculation.py         ← Pydantic schemas
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py             ← SQLAlchemy engine + session
│   │   └── base.py                ← Base declarative
│   └── core/
│       ├── __init__.py
│       ├── config.py              ← Variables de entorno
│       └── security.py            ← Funciones de autenticación
├── engine/                        ← MOTOR DE CÁLCULO (separado de API)
│   ├── __init__.py
│   ├── acoustic_engine.py         ← Clase AcousticEngine
│   ├── materials.py               ← Librería de materiales
│   ├── calculations/
│   │   ├── __init__.py
│   │   ├── sharp.py               ← Fórmula de Sharp
│   │   ├── iso717_1.py            ← Ponderación ISO 717-1
│   │   └── utils.py               ← Utilidades matemáticas
│   └── tests/
│       ├── __init__.py
│       ├── test_acoustic_engine.py
│       └── test_materials.py
├── Dockerfile
├── requirements.txt               ← Todas las deps de Python
└── pytest.ini

frontend/
├── app/
│   ├── layout.tsx                 ← Layout raíz
│   ├── page.tsx                   ← Home page
│   ├── (dashboard)/
│   │   ├── layout.tsx
│   │   └── page.tsx               ← Dashboard de proyectos
│   ├── projects/
│   │   ├── layout.tsx
│   │   ├── page.tsx               ← Listado de proyectos
│   │   ├── new/
│   │   │   └── page.tsx           ← Crear proyecto
│   │   └── [id]/
│   │       ├── page.tsx           ← Ver proyecto + calculadora
│   │       └── edit/
│   │           └── page.tsx       ← Editar proyecto
│   └── api/                       ← API routes si necesitas
│       └── health.ts
├── components/
│   ├── Header.tsx
│   ├── Navigation.tsx
│   ├── ProjectCard.tsx
│   ├── Calculator/
│   │   ├── index.tsx              ← Componente calculadora
│   │   ├── MaterialSelector.tsx
│   │   ├── ResultsDisplay.tsx
│   │   └── Chart.tsx
│   └── ui/
│       ├── Button.tsx
│       ├── Input.tsx
│       └── Card.tsx
├── lib/
│   ├── api.ts                     ← Cliente HTTP (fetch wrapper)
│   └── utils.ts
├── styles/
│   └── globals.css
├── public/
│   └── (favicons, images, etc)
├── Dockerfile
├── package.json
├── tsconfig.json
├── next.config.js
├── tailwind.config.js
└── .eslintrc.json

.devcontainer/
├── devcontainer.json              ← Configuración para Codespaces
├── post-create.sh                 ← Script de inicialización
└── Dockerfile (opcional)

.github/
└── workflows/
    └── ci.yml                     ← Tests + linting automáticos

Archivos raíz:
├── docker-compose.yml             ← Orquestación de servicios
├── .gitignore
├── .env.example
├── README.md
└── DEVELOPMENT.md                 ← Guía para desarrolladores

2) **Archivos con contenido inicial (no vacíos):**

a) requirements.txt:
   - FastAPI==0.115.0
   - uvicorn[standard]==0.30.0
   - SQLAlchemy==2.1.0
   - psycopg2-binary==2.9.10
   - pydantic==2.8.0
   - pydantic-settings==2.4.0
   - alembic==1.14.0
   - pytest==8.2.0
   - pytest-asyncio==0.24.0
   - numpy==1.26.0
   - scipy==1.14.0
   - python-dotenv==1.0.1

b) docker-compose.yml:
   - Servicio PostgreSQL (port 5432)
   - Servicio Backend (port 8000)
   - Servicio Frontend (port 3000)
   - Red personalizada
   - Volúmenes para desarrollo (hot-reload)

c) backend/Dockerfile:
   - Base: python:3.11-slim
   - CMD: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

d) frontend/Dockerfile:
   - Base: node:18-alpine
   - CMD: npm run dev

e) backend/app/main.py:
   - FastAPI() initialized
   - CORS enabled
   - Health check endpoint (GET /health)
   - Routers importados (projects, calculations, auth)

f) .devcontainer/devcontainer.json:
   - Features: Docker-in-Docker, Node 18, Python 3.11
   - Post-create script
   - Extensiones de VS Code
   - Forward ports: 3000, 8000, 5432

g) .devcontainer/post-create.sh:
   - pip install -r backend/requirements.txt
   - cd frontend && npm install
   - docker-compose up -d
   - Espera a que PostgreSQL esté listo
   - Muestra instrucciones

h) Dockerfile de PostgreSQL: No es necesario (usamos imagen oficial)

3) **Contenido mínimo de cada archivo Python/TS:**

- Comentarios explicativos
- Imports organizados
- Type hints (Python + TypeScript)
- Docstrings en funciones principales
- Ejemplos de uso (comments)

4) **Resultado esperado:**

   Cuando termine, debería poder:
   a) git clone mi-repo
   b) cd mi-repo
   c) docker-compose up -d
   d) Ver logs: "PostgreSQL ready", "Backend running", "Frontend compiled"
   e) Acceder a http://localhost:3000 (Next.js landing page)
   f) Acceder a http://localhost:8000/docs (Swagger UI)

IMPORTANTE: 
- Crea TODOS los archivos en una sola ejecución
- Usa estructura de carpetas exacta como especifiqué
- No dejes archivos "TODO" sin crear
- Documenta cada archivo con comentarios claros
- Asegúrate de que docker-compose.yml sea funcional
```

### Qué esperar

Después de que Claude Code ejecute este prompt:

✅ **~60-70 archivos creados**  
✅ **Estructura lista para desarrollo**  
✅ **docker-compose.yml funcional**  
✅ **Endpoints base en FastAPI**  
✅ **Componentes base en Next.js**

---

## 2. Motor de cálculo (ISO 12354-1)

### Contexto previo (copia en chat para referencia)

```
Ya tengo la estructura base del proyecto.
Ahora voy a implementar el motor de cálculos acústicos.

Mi proyecto usan:
- Backend en backend/engine/ (separado de la API)
- Cálculos de aislamiento acústico con ISO 12354-1 y ISO 717-1
- Entrada: lista de materiales (nombre, espesor)
- Salida: R(f) por frecuencia + Rw (índice único ponderado)
- Frecuencias de análisis: 1/3 octava desde 100 Hz a 5000 Hz
```

### Prompt para AcousticEngine

```
Implementa el motor principal de cálculos acústicos.

UBICACIÓN: backend/engine/acoustic_engine.py

CLASE: AcousticEngine

MÉTODOS NECESARIOS:

1) __init__(self, config: dict = None)
   - Parámetro config (opcional): para personalizar constantes
   - Inicializa librería de materiales
   - Ready para calcular

2) calcular_aislamiento(
     materiales: List[Dict[str, float]], 
     frecuencias: List[float] = None
   ) -> Dict[float, float]
   
   ENTRADA:
   - materiales: [
       {"nombre": "Hormigón 200mm", "espesor": 0.2},
       {"nombre": "Lana mineral 50mm", "espesor": 0.05}
     ]
   - frecuencias (opcional): [125, 250, 500, 1000, 2000, 4000]
   
   LÓGICA:
   - Si no se pasan frecuencias, usa 1/3 octava estándar (100-5000 Hz)
   - Para cada material: obtener R(f) usando fórmula de Sharp
   - Para múltiples capas: R_total(f) = suma de R_i(f)
   - Devolver dict {frecuencia: R_dB}
   
   SALIDA:
   {
     125: 28.5,
     250: 32.1,
     500: 38.7,
     1000: 42.3,
     2000: 45.8,
     4000: 48.2
   }
   
   VALIDACIÓN:
   - Verificar que materiales existan en librería (si no, excepción)
   - Verificar que espesores sean > 0
   - Catch de excepciones del cálculo → raise AcousticEngineError

3) ponderacion_iso717_1(
     R_frecuencias: Dict[float, float]
   ) -> Dict[str, float]
   
   ENTRADA:
   - Dict con R(f) de método anterior
   
   LÓGICA:
   - Usar curva de referencia de ISO 717-1 (está documentada)
   - Aplicar desplazamiento: buscar valor que minimice desviaciones
   - Calcular Rw (índice único)
   - Calcular C (adaptación tráfico) - diferencia a 100 Hz
   - Calcular Ctr (adaptación ferrocarril) - diferencia a 500 Hz
   
   SALIDA:
   {
     "Rw": 44,
     "C": -3,
     "Ctr": -8,
     "desviaciones_max": 2.1,
     "R_ponderado": {...}  # R(f) + curva referencia
   }
   
   REFERENCIAS:
   - Curva ISO 717-1: https://en.wikipedia.org/wiki/Sound_reduction_index
   - Frecuencias: 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000

4) obtener_material(nombre: str) -> Dict
   - Busca en librería de materiales
   - Si existe: devuelve propiedades (densidad, factor_pérdida, etc)
   - Si no existe: raise MaterialNotFoundError

VALIDACIONES Y ERRORES:

Crear excepciones personalizadas:
- AcousticEngineError (base)
- MaterialNotFoundError
- CalculationError

EJEMPLO DE USO (al final del archivo):

if __name__ == "__main__":
    engine = AcousticEngine()
    
    # Caso simple: muro de hormigón
    muro = [{"nombre": "Hormigón 200mm", "espesor": 0.2}]
    R_f = engine.calcular_aislamiento(muro)
    print(f"R(f): {R_f}")
    
    # Ponderación
    resultado = engine.ponderacion_iso717_1(R_f)
    print(f"Rw: {resultado['Rw']} dB")
    print(f"C: {resultado['C']} dB")

DOCUMENTACIÓN:

- Docstring en cada método (Google style)
- Explicar fórmula de Sharp brevemente (referencias a ISO 12354-1)
- Type hints completos
```

### Prompt para módulo de materiales

```
Implementa la librería de materiales acústicos.

UBICACIÓN: backend/engine/materials.py

CLASE: Material

PROPIEDADES:
- nombre: str
- densidad: float (kg/m³)
- espesor: float (m)
- factor_perdida: float (adimensional, 0-1)
- tipo: str ("poroso", "rígido", "composite")

MÉTODOS:
- __init__(nombre, densidad, factor_pérdida, tipo)
- __repr__() → "Material(nombre='Hormigón', ρ=2400 kg/m³)"

CLASE: LibreriaMatariales

CONSTRUCTOR:
- Inicializa un dict con ~50 materiales estándar

MÉTODOS:
1) agregar_material(material: Material) → None
2) buscar_por_nombre(nombre: str) -> Material
3) buscar_por_tipo(tipo: str) -> List[Material]
4) listar_todos() -> List[Dict]

BASE DE DATOS DE MATERIALES (50 items):

Porosos (lana mineral, espuma, corcho):
- "Lana mineral 50mm" → ρ=30, f=0.1
- "Espuma acústica 25mm" → ρ=40, f=0.15
- "Corcho natural 30mm" → ρ=120, f=0.08

Rígidos (hormigón, ladrillo, gypsum):
- "Hormigón 200mm" → ρ=2400, f=0.02
- "Ladrillo cerámico 120mm" → ρ=1800, f=0.03
- "Yeso + papel 13mm" → ρ=900, f=0.01

Composites (dobles capas):
- "Doble vidrio 4-12-4" → ρ=800 (equivalente), f=0.06
- "Ladrillo 120 + lana 50" → ρ=900 (equivalente), f=0.05

EJEMPLO DE USO:

libreria = LibreriaMatariales()

# Búsqueda
material = libreria.buscar_por_nombre("Hormigón 200mm")
print(material.densidad)  # 2400

# Listar todos
todos = libreria.listar_todos()
for mat in todos[:5]:
    print(mat)

VALIDACIONES:
- Material no puede tener densidad <= 0
- Factor de pérdida entre 0 y 1
- Nombre no puede estar vacío o duplicado
```

### Prompt para cálculos (Sharp + ISO 717-1)

```
Implementa los cálculos matemáticos de aislamiento acústico.

UBICACIÓN: backend/engine/calculations/

ARCHIVO 1: sharp.py

FUNCIÓN: calcular_r_sharp(
  material: Material,
  frecuencia: float
) -> float

FÓRMULA (Sharp):
Para materiales porosos:
  R(f) = 0.0571 * log10(ρ * d * f) + 10

Para materiales rígidos:
  R(f) = 20 * log10(ρ * d * f / 2e5) + 10

DONDE:
- ρ = densidad (kg/m³)
- d = espesor (m)
- f = frecuencia (Hz)

ENTRADA:
- Material object
- Frecuencia en Hz

SALIDA:
- R en dB (float)

VALIDACIONES:
- f > 0
- Validar tipo de material
- Retornar 0 si resultado es negativo (no hay aislamiento)

---

ARCHIVO 2: iso717_1.py

FUNCIÓN: aplicar_ponderacion_iso717_1(
  R_frecuencias: Dict[float, float]
) -> Dict[str, Any]

CONSTANTES ISO 717-1:

Curva de referencia (valores de ponderación por frecuencia):
FRECUENCIA (Hz) | CURVA_REFERENCIA (dB)
100             | 30
125             | 35
160             | 40
200             | 42
250             | 44
315             | 45
400             | 46
500             | 47
630             | 48
800             | 48
1000            | 48
1250            | 48
1600            | 49
2000            | 49
2500            | 50
3150            | 50
4000            | 51
5000            | 52

LÓGICA:
1) Interpolar la curva de referencia a las frecuencias de R
2) Buscar el desplazamiento "offset" que minimiza:
   suma( max(0, referencia - (R + offset)) )
3) Rw = 50 (frecuencia 2000 Hz) + offset
4) Calcular C (diferencia a 100 Hz)
5) Calcular Ctr (diferencia a 500 Hz)

SALIDA:
{
  "Rw": 44,        # Índice único
  "C": -3,         # Adaptación tráfico carretero
  "Ctr": -8,       # Adaptación ferrocarril
  "offset": 2.5,   # Desplazamiento aplicado
  "max_desviacion": 1.8,  # Desviación máxima
  "R_ponderado": {...}    # R + offset para cada f
}

REFERENCIAS:
- https://en.wikipedia.org/wiki/Weighted_sound_reduction_index
- ISO 717-1:2020

---

ARCHIVO 3: utils.py

FUNCIONES AUXILIARES:
- interpolar_frecuencias(R_dict, frecuencias_target) → Dict
- log10_seguro(valor) → float (evita log de 0)
- redondear_iso717(valor) → int (reglas de redondeo ISO)
- generar_frecuencias_estandar() → List[float]
```

### Tests para el motor

```
Crea tests unitarios para el motor.

UBICACIÓN: backend/engine/tests/

ARCHIVO: test_acoustic_engine.py

TEST CASES:

1) test_material_simple
   - Crear motor
   - Calcular aislamiento para hormigón 200mm único
   - Verificar que R(1000 Hz) > 40 dB
   - Verificar que R es creciente con frecuencia

2) test_material_no_existe
   - Intentar calcular con material inexistente
   - Debe lanzar MaterialNotFoundError

3) test_ponderacion_iso717
   - Calcular R(f) simple
   - Aplicar ponderación
   - Verificar que Rw está en rango razonable (30-70 dB)

4) test_multiples_capas
   - 3 materiales diferentes
   - Verificar que R_total > R_individual

5) test_validaciones
   - Espesor negativo → error
   - Frecuencia cero → error
   - Material vacío → error

FIXTURES:
- motor (AcousticEngine instance)
- material_hormigon
- material_lana
- R_frecuencias_muestra

COMANDO PARA EJECUTAR:
pytest backend/engine/tests/ -v --cov=backend.engine
```

---

## 3. Integración con API FastAPI

### Prompt para endpoints de cálculos

```
Crea los endpoints FastAPI para exponer el motor de cálculos.

UBICACIÓN: backend/app/api/calculations.py

SCHEMAS PYDANTIC:

1) class MaterialInput(BaseModel):
   nombre: str
   espesor: float
   
   class Config:
     example = {"nombre": "Hormigón 200mm", "espesor": 0.2}

2) class CalculationRequest(BaseModel):
   proyecto_id: int
   nombre: str
   materiales: List[MaterialInput]
   frecuencias: Optional[List[float]] = None
   
   class Config:
     example = {
       "proyecto_id": 1,
       "nombre": "Muro principal",
       "materiales": [{"nombre": "Hormigón 200mm", "espesor": 0.2}],
       "frecuencias": [125, 250, 500, 1000, 2000, 4000]
     }

3) class CalculationResponse(BaseModel):
   id: int
   proyecto_id: int
   nombre: str
   entrada: CalculationRequest
   salida: Dict[str, Any]  # {Rw, C, Ctr, R_frecuencias, etc}
   timestamp: datetime
   
   class Config:
     from_attributes = True

ENDPOINTS:

1) POST /api/calculations/
   - Recibe CalculationRequest
   - Validación Pydantic automática
   - Llama a AcousticEngine.calcular_aislamiento()
   - Llama a AcousticEngine.ponderacion_iso717_1()
   - Crea registro en BD (Calculation model)
   - Devuelve CalculationResponse con ID
   - Status 201 Created
   - Manejo de errores: 422 (validación), 500 (cálculo)

2) GET /api/calculations/{id}
   - Busca cálculo por ID en BD
   - Devuelve CalculationResponse
   - 404 si no existe

3) GET /api/calculations/proyecto/{proyecto_id}
   - Lista todos los cálculos de un proyecto
   - Query params: ?limit=10&offset=0
   - Devuelve List[CalculationResponse]

4) DELETE /api/calculations/{id}
   - Elimina un cálculo (soft delete)
   - 204 No Content

INTEGRACIÓN CON BD:

- Importa Session de db.session
- Usar dependency injection de FastAPI: def get_db() -> Session:
- Crear Calculation object:
  calc = Calculation(
    proyecto_id=req.proyecto_id,
    nombre=req.nombre,
    entrada_json=json.dumps(req.dict()),
    resultado_json=json.dumps(resultado),
    timestamp=datetime.now()
  )
- db.add(calc)
- db.commit()
- db.refresh(calc)

MANEJO DE ERRORES:

try:
  resultado = engine.calcular_aislamiento(...)
  resultado = engine.ponderacion_iso717_1(resultado)
except MaterialNotFoundError as e:
  raise HTTPException(status_code=400, detail=str(e))
except CalculationError as e:
  raise HTTPException(status_code=500, detail="Error en cálculo")
except Exception as e:
  logger.error(f"Error inesperado: {e}")
  raise HTTPException(status_code=500, detail="Error interno")

LOGS:

- Usar logging.getLogger(__name__)
- Log CADA request: logger.info(f"POST /calculations: {req.nombre}")
- Log CADA error: logger.error(f"Cálculo fallido: {e}")

TESTS:

Agregar tests en backend/tests/api/test_calculations.py:
- test_post_calculation_exitoso()
- test_post_calculation_material_invalido()
- test_get_calculation_por_id()
- test_get_calculations_por_proyecto()
- test_delete_calculation()

Usar client de FastAPI: from fastapi.testclient import TestClient
```

### Prompt para crear modelo Calculation en BD

```
Crea el modelo SQLAlchemy para almacenar resultados de cálculos.

UBICACIÓN: backend/app/models/calculation.py

MODELO: Calculation

COLUMNAS:
- id: Integer, primary key, autoincrement
- proyecto_id: Integer, foreign key → Project.id, not null
- nombre: String(255), not null
- entrada_json: Text (JSON serializado del request)
- resultado_json: Text (JSON del cálculo: Rw, C, Ctr, R(f))
- timestamp: DateTime, default=utcnow, not null
- actualizado_en: DateTime, onupdate=utcnow
- eliminado: Boolean, default=False (soft delete)

RELACIONES:
- proyecto: relationship("Project", back_populates="calculations")

MÉTODOS:
- __repr__() → f"Calculation({self.nombre}, Rw={self.resultado['Rw']} dB)"
- to_dict() → Dict con todos los campos

ÍNDICES:
- idx_proyecto_id (búsquedas frecuentes por proyecto)
- idx_timestamp (ordenar por fecha)

EJEMPLO:

calc = Calculation(
  proyecto_id=1,
  nombre="Muro principal",
  entrada_json='{"materiales": [...], "frecuencias": [...]}',
  resultado_json='{"Rw": 44, "C": -3, ...}'
)
db.add(calc)
db.commit()
```

---

## 4. Tests unitarios

### Prompt para suite de tests

```
Genera una suite completa de tests con pytest.

ESTRUCTURA:

backend/tests/
├── __init__.py
├── conftest.py                    ← Fixtures compartidas
├── test_engine.py                 ← Tests del motor
└── api/
    ├── __init__.py
    └── test_calculations.py       ← Tests de endpoints

ARCHIVO: conftest.py

Fixtures:
- @pytest.fixture
  def engine() -> AcousticEngine:
    return AcousticEngine()

- @pytest.fixture
  def material_test() -> Material:
    return Material("Hormigón 200mm", densidad=2400, factor_pérdida=0.02)

- @pytest.fixture
  def client() -> TestClient:
    from app.main import app
    return TestClient(app)

- @pytest.fixture
  def db_session():
    # Crea BD temporal para tests
    # Carga fixtures de datos
    # Cleanup después
    pass

TEST CASES (en test_engine.py):

1) TestAcousticEngine:
   - test_init
   - test_calcular_simple
   - test_calcular_multiples_capas
   - test_calcular_frecuencias_custom
   - test_ponderacion_iso717
   - test_error_material_inexistente
   
2) TestMateriales:
   - test_buscar_por_nombre
   - test_lista_vacia
   - test_agregar_material_duplicado

TEST CASES (en api/test_calculations.py):

1) test_post_calculation_201
2) test_post_invalid_material_400
3) test_get_calculation_200
4) test_get_nonexistent_404
5) test_list_by_project_200

CONFIGURACIÓN:

pytest.ini:
[pytest]
testpaths = backend/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    unit: Tests unitarios
    integration: Tests de integración
    slow: Tests lentos

COMANDOS:

# Todos los tests
pytest backend/tests

# Solo unitarios
pytest backend/tests -m unit

# Con cobertura
pytest backend/tests --cov=backend.app --cov=backend.engine

# Watch mode (requiere pytest-watch)
ptw backend/tests
```

---

## 5. Frontend React

### Prompt para componente Calculator

```
Crea el componente React principal para la calculadora acústica.

UBICACIÓN: frontend/components/Calculator/index.tsx

COMPONENTE: Calculator

RESPONSABILIDADES:
1) Seleccionar materiales (dropdown con búsqueda)
2) Ingresar espesor de cada material
3) Botón "Calcular"
4) Mostrar gráfico de R(f)
5) Mostrar tarjeta con resultados (Rw, C, Ctr)

ESTRUCTURA:

interface Material {
  nombre: string;
  densidad: number;
  tipoMaterial: string;
}

interface MaterialSeleccionado extends Material {
  espesor: number;
}

interface Resultado {
  Rw: number;
  C: number;
  Ctr: number;
  R_frecuencias: Record<number, number>;
}

ESTADO:
- materiales_seleccionados: MaterialSeleccionado[]
- frecuencias: number[] (opcional, por defecto 1/3 octava)
- resultado: Resultado | null
- cargando: boolean
- error: string | null

FUNCIONES:
- agregarMaterial(material: Material): void
  └ Agrega material con espesor inicial (0.1m)
  
- actualizarEspesor(index: number, espesor: number): void
  └ Actualiza espesor de material en posición index
  
- eliminarMaterial(index: number): void
  └ Remueve material de la lista
  
- calcular(): Promise<void>
  └ POST /api/calculations con datos actuales
  └ Maneja cargando, error, resultado
  
- buscarMateriales(query: string): Promise<Material[]>
  └ GET /api/materiales?search=query

INTERFAZ (mockup):

┌────────────────────────────────────────┐
│  📐 Calculadora Acústica              │
├────────────────────────────────────────┤
│                                        │
│ Selecciona materiales:                 │
│ [Buscar material...      ]             │
│ ┌─ Hormigón 200mm        0.2m [❌]    │
│ ├─ Lana mineral 50mm     0.05m [❌]   │
│ └─ Vidrio 4-12-4         0.02m [❌]   │
│                                        │
│ [Agregar material +]                   │
│                                        │
│              [CALCULAR]                │
│                                        │
├────────────────────────────────────────┤
│  RESULTADOS:                           │
│  Rw = 45 dB │ C = -3 │ Ctr = -8      │
├────────────────────────────────────────┤
│  [Gráfico R(f)]                        │
│   Y axis: R (dB)                       │
│   X axis: Frecuencia (Hz)              │
│   Línea azul: valores calculados       │
│   Línea gris: curva ISO 717-1          │
└────────────────────────────────────────┘

ESTILOS:
- Tailwind CSS
- Componentes reutilizables (Button, Input, Card)
- Dark mode ready
- Responsive (mobile-first)

TESTING:
- render(<Calculator />)
- user.click(agregar material button)
- expect(find material in list)
- submit form → mock API
- assert resultado rendered

EJEMPLO:

export function Calculator() {
  const [materiales, setMateriales] = useState<MaterialSeleccionado[]>([]);
  const [resultado, setResultado] = useState<Resultado | null>(null);
  const [cargando, setCargando] = useState(false);

  const calcular = async () => {
    setCargando(true);
    try {
      const res = await fetch("/api/calculations", {
        method: "POST",
        body: JSON.stringify({ materiales })
      });
      if (!res.ok) throw new Error(res.statusText);
      const data = await res.json();
      setResultado(data.salida);
    } catch (e) {
      console.error(e);
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="space-y-6 p-6">
      {/* Selector de materiales */}
      {/* Inputs de espesor */}
      {/* Botón calcular */}
      {resultado && <ResultsDisplay resultado={resultado} />}
      {resultado && <Chart R_frecuencias={resultado.R_frecuencias} />}
    </div>
  );
}
```

---

## 6. CI/CD con GitHub Actions

### Prompt para workflow

```
Configura GitHub Actions para CI/CD.

UBICACIÓN: .github/workflows/ci.yml

TRIGGERS:
- push a main
- push a develop
- pull requests

JOBS:

1) JOB: test-backend
   Steps:
   - Checkout code
   - Setup Python 3.11
   - Cache pip dependencies
   - Install requirements
   - Run flake8 (linting)
   - Run black (format check)
   - Run pytest with coverage
   - Upload coverage to Codecov (opcional)
   - Fail si coverage < 80%

2) JOB: test-frontend
   Steps:
   - Checkout code
   - Setup Node 18
   - Cache npm dependencies
   - npm ci
   - npm run lint
   - npm run build
   - npm run test (si existen tests)
   - Fail si build falla

3) JOB: build-docker (optional, solo en main)
   Condition: if: github.ref == 'refs/heads/main'
   Steps:
   - Setup Docker Buildx
   - Build backend image
   - Build frontend image
   - Push a Docker registry (opcional: Docker Hub, GHCR)

REQUISITOS:
- Secrets para Docker registry (si aplica)
- CODECOV_TOKEN para reportes

MATRIZ TESTS (opcional, para múltiples Python versions):
strategy:
  matrix:
    python-version: ["3.9", "3.10", "3.11"]

NOTIFICACIONES:
- Fail: notifica en PR comment
- Success: comment "✅ Todos los tests pasaron"
```

---

## 📋 Template de issue/PR

Crea un template para que tengas claro qué hacer en cada tarea:

**`.github/ISSUE_TEMPLATE/feature.md`:**

```markdown
## 🎯 Descripción
[Qué se debe implementar]

## 📋 Tareas
- [ ] Implementación backend
- [ ] Tests backend
- [ ] Integración API
- [ ] Frontend (si aplica)
- [ ] Tests frontend
- [ ] Documentación
- [ ] Merge a main

## 🔗 Contexto
[Links, referencias, notas]

## ✅ Checklist
- [ ] Código sigue PEP 8 / ESLint
- [ ] Tests pasan con cobertura > 80%
- [ ] Docker compose up -d levanta sin errores
- [ ] Sin console.error en navegador
- [ ] Documentado en DEVELOPMENT.md
```

---

## 🚀 Resumen: Flujo de prompts recomendado

```
DÍA 1 (Mañana):
└─ Prompt #1: Scaffolding completo

DÍA 1 (Tarde):
└─ Prompt #2a: AcousticEngine
└─ Prompt #2b: LibreriaMatariales
└─ Prompt #2c: sharp.py + iso717_1.py
└─ Prompt #2d: Tests del motor

DÍA 2 (Mañana):
└─ Prompt #3a: Endpoints de cálculos
└─ Prompt #3b: Modelo Calculation en BD
└─ Prompt #4: Tests de API

DÍA 2 (Tarde):
└─ Prompt #5: Componente Calculator
└─ Prompt #6: GitHub Actions CI/CD

DÍA 3:
└─ Integration testing
└─ Deploy a Codespaces / local
└─ Demo funcional
```

---

## 📚 Links útiles

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/)
- [Pydantic v2](https://docs.pydantic.dev/)
- [Next.js App Router](https://nextjs.org/docs/app)
- [pytest Best Practices](https://docs.pytest.org/)
- [ISO 717-1:2020](https://www.iso.org/standard/70967.html) (especificación oficial)
- [Sharp's Method](https://en.wikipedia.org/wiki/Sound_reduction_index)

---

**Última actualización:** Mayo 2026
