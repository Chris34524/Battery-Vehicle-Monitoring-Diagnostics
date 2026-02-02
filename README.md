# Battery & Vehicle Monitoring & Diagnostics — FastAPI + PostgreSQL (Docker)

Backend MVP para **capturar telemetría** (SoC, SoH, voltajes/corrientes, temperaturas, odómetro) y entregar:
- **Health check** (`/api/health`)
- **Ingesta** de telemetría en lote (`POST /api/telemetry`)
- **Último estado** por VIN (`GET /api/vehicles/{vin}/latest`)
- **Resumen** por rango de tiempo (`GET /api/vehicles/{vin}/summary?from_ts=...&to_ts=...`)

Incluye **Docker Compose** (API + Postgres), y un script **demo reproducible** (`scripts/demo.sh`).

---

## Stack
- Python 3.11+ (compatible 3.10+)
- FastAPI + Uvicorn
- PostgreSQL 16 (Docker)
- SQLAlchemy 2 + psycopg3
- (Opcional) TimescaleDB Extension (si está disponible)

---

## Estructura del repo

```text
Battery-Vehicle-Monitoring-Diagnostics/
├─ backend/
│  ├─ main.py
│  ├─ db.py
│  ├─ models.py
│  ├─ schemas.py
│  └─ services.py
├─ scripts/
│  └─ demo.sh
├─ Dockerfile
├─ docker-compose.yml
├─ requirements.txt
└─ README.md
```

> Nota: si tu repo todavía no tiene `db.py/models.py/schemas.py/services.py`, ajústalo al árbol real.  
> Lo importante es que el entrypoint de Uvicorn apunte a `backend.main:app`.

---

## Requisitos
- **Docker Desktop** (recomendado para correr todo igual en cualquier PC)
- Git Bash (Windows) o Bash (Linux/Mac) para ejecutar `scripts/demo.sh`

---

## Quickstart (Docker Compose)

Desde la raíz del repo:

```bash
docker compose up -d --build
docker compose ps
```

Abre:
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/api/health

Luego corre el demo:

```bash
chmod +x scripts/demo.sh
./scripts/demo.sh
```

---

## Variables de entorno

El backend se conecta a Postgres usando `DATABASE_URL` (recomendado).

**Dentro de Docker Compose (API → DB):**
- Host DB: `battery-db`
- Puerto DB: `5432`

Ejemplo de `DATABASE_URL` usado en `docker-compose.yml`:

```text
postgresql+psycopg://postgres:postgres@battery-db:5432/battery
```

**Desde tu PC (host) hacia el contenedor de Postgres:**
- Host: `localhost`
- Puerto: `5434` (según tu mapeo `5434:5432`)

Ejemplo (para herramientas externas):
```text
postgresql://postgres:postgres@localhost:5434/battery
```

---

## Cómo correr sin Docker (modo local)

> Útil si quieres debuggear rápido en tu IDE, pero manteniendo la DB en Docker.

1) Levanta solo Postgres:

```bash
docker compose up -d battery-db
```

2) Crea venv e instala dependencias:

```bash
python -m venv .venv
source .venv/Scripts/activate   # Git Bash Windows
pip install -r requirements.txt
```

3) Exporta `DATABASE_URL` apuntando a tu Postgres local (puerto 5434):

```bash
export DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5434/battery"
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

En PowerShell:

```powershell
$env:DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5434/battery"
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Endpoints principales

### 1) Health

```bash
curl http://localhost:8000/api/health
```

Respuesta esperada:

```json
{"status":"OK","db":"OK"}
```

---

### 2) Ingest telemetry (batch)

**POST** `/api/telemetry`  
Body: lista JSON (array) con telemetría.

```bash
curl -s -X POST "http://localhost:8000/api/telemetry"   -H "Content-Type: application/json"   -d '[
    {"vin":"VIN-DEMO-001","ts":"2026-01-24T12:05:00Z","soc":18.0,"soh":92.0,"pack_voltage":310.1,"pack_current":95.0,"max_temp":52.0,"min_temp":33.0,"odo_km":1201.2},
    {"vin":"VIN-DEMO-001","ts":"2026-01-24T12:10:00Z","soc":35.5,"soh":92.0,"pack_voltage":315.0,"pack_current":70.0,"max_temp":32.0,"min_temp":24.0,"odo_km":1201.8}
  ]'
```

Respuesta:

```json
{"inserted":2}
```

---

### 3) Latest por VIN

**GET** `/api/vehicles/{vin}/latest`

```bash
curl -s "http://localhost:8000/api/vehicles/VIN-DEMO-001/latest"
```

Respuesta (ejemplo):

```json
{
  "vin": "VIN-DEMO-001",
  "ts": "2026-01-24T12:10:00Z",
  "soc": 35.5,
  "soh": 92.0,
  "pack_voltage": 315.0,
  "pack_current": 70.0,
  "power_kw": 22.05,
  "max_temp": 32.0,
  "min_temp": 24.0,
  "odo_km": 1201.8,
  "alerts": []
}
```

---

### 4) Summary por rango de tiempo

**GET** `/api/vehicles/{vin}/summary?from_ts=...&to_ts=...`

```bash
curl -s "http://localhost:8000/api/vehicles/VIN-DEMO-001/summary?from_ts=2026-01-24T11:59:00Z&to_ts=2026-01-24T12:10:00Z"
```

Respuesta (ejemplo):

```json
{
  "vin": "VIN-DEMO-001",
  "from_ts": "2026-01-24T11:59:00Z",
  "to_ts": "2026-01-24T12:10:00Z",
  "samples": 2,
  "soc_min": 18.0,
  "soc_max": 35.5,
  "temp_max": 52.0,
  "temp_min": 24.0
}
```

---

## Demo reproducible (scripts/demo.sh)

Ejecuta:

```bash
chmod +x scripts/demo.sh
./scripts/demo.sh
```

El script normalmente hace:
1) Espera a que la API responda en `/api/health`
2) Inserta 2 muestras de telemetría
3) Consulta `/latest`
4) Consulta `/summary`

---

## Cómo leer los bloques `bash` y `json` en este README

### Bloques `bash`
Son **comandos** para ejecutar en tu terminal.

- `docker compose up -d --build`  
  Construye imágenes y levanta servicios en segundo plano.
- `curl ...`  
  Hace una petición HTTP para probar endpoints.

> Tip: si un comando falla, corre primero `docker compose ps` y `docker compose logs -f battery-api` para ver qué está pasando.

### Bloques `json`
Son **ejemplos del body o respuestas** de la API.

- En `POST /api/telemetry`, el body es un **array** (lista) de objetos:
  - cada objeto es una lectura de telemetría
  - `ts` debe ser ISO-8601 (por ejemplo, `2026-01-24T12:10:00Z`)

---

## Troubleshooting rápido

### “Connection refused” en localhost:8000
- Verifica que el contenedor está arriba:
  ```bash
  docker compose ps
  ```
- Revisa logs:
  ```bash
  docker compose logs -f battery-api
  ```

### Te da 404 en endpoints
- Abre Swagger y valida rutas reales:
  - http://localhost:8000/docs
- Si cambiaste rutas en `backend/main.py`, actualiza `scripts/demo.sh` para que apunte a las rutas correctas.

### TimescaleDB
Tu `startup()` intenta:
- `CREATE EXTENSION IF NOT EXISTS timescaledb;`
- `create_hypertable(...)`

Si tu imagen es `postgres:16` (sin Timescale), tu código ya lo tolera con `try/except` y **no debería romper** el MVP.

---

## Roadmap para 5/5 (pulido)
- Agregar `.env.example` y leer `.env` con `python-dotenv`
- Agregar paginación/filtrado por VIN y rango
- Agregar endpoint de “anomalías” (reglas) por VIN
- Agregar CI (GitHub Actions) y badge en README
