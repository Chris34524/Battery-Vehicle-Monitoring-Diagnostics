# Battery & Vehicle Monitoring & Diagnostics

## Descripción

Servicio para centralizar y analizar datos de batería y vehículo
(voltaje, corriente, temperatura, SoC, SoH, códigos de falla, etc.) como base
para diagnóstico y monitoreo de la salud de los packs.

Este proyecto está pensado como base para estimar condiciones de operación y,
a futuro, métricas como State of Health (SoH) y Remaining Useful Life (RUL).

## Estado actual (MVP técnico end-to-end)

Backend FastAPI (`backend/main.py`) con:

- `GET /health`
  - Verifica que el servicio está vivo.

- `POST /telemetry/mock?count=N`
  - Genera N registros de telemetría simulados para un VIN de prueba.
  - Guarda los registros en memoria.

- `GET /telemetry/latest?limit=N`
  - Devuelve los últimos N registros en memoria.

Ejemplo de registro de telemetría:

```json
{
  "vin": "LDRTESTBAT123456789",
  "timestamp": "2025-12-16T12:34:56.000Z",
  "voltage_v": 640.0,
  "current_a": 120.0,
  "temperature_c": 26.5,
  "soc_percent": 85.0,
  "soh_percent": 98.0,
  "error_code": null
}
