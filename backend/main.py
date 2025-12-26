from datetime import datetime, timedelta
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(
    title="Battery & Vehicle Monitoring API",
    version="0.1.0",
)


class TelemetryRecord(BaseModel):
    vin: str = Field(..., description="VIN del vehículo")
    timestamp: datetime = Field(..., description="Fecha/hora de la medición (UTC)")
    voltage_v: float = Field(..., description="Voltaje del pack [V]")
    current_a: float = Field(..., description="Corriente [A] (signo puede indicar carga/descarga)")
    temperature_c: float = Field(..., description="Temperatura del pack [°C]")
    soc_percent: float = Field(..., ge=0, le=100, description="State of Charge [%]")
    soh_percent: float = Field(..., ge=0, le=100, description="State of Health [%]")
    error_code: str | None = Field(
        None, description="Código de falla si aplica (por ejemplo: BMS_OVERVOLTAGE)"
    )


# "Base de datos" en memoria
TELEMETRY_DATA: List[TelemetryRecord] = []


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "battery-vehicle-monitoring-api",
        "version": "0.1.0",
    }


@app.post("/telemetry/mock", response_model=List[TelemetryRecord])
def generate_mock_telemetry(count: int = 10):
    """
    Genera datos de telemetría simulados para un VIN de prueba
    y los guarda en memoria.
    """
    global TELEMETRY_DATA
    TELEMETRY_DATA.clear()

    base_time = datetime.utcnow()
    vin = "LDRTESTBAT123456789"

    for i in range(count):
        record = TelemetryRecord(
            vin=vin,
            timestamp=base_time - timedelta(minutes=(count - i) * 5),
            voltage_v=640.0 - i * 0.5,     # pequeña variación de voltaje
            current_a=120.0 - i * 1.5,     # corriente bajando un poco
            temperature_c=25.0 + i * 0.2,  # temperatura sube ligeramente
            soc_percent=90.0 - i * 0.8,    # SOC bajando con el tiempo
            soh_percent=98.0,              # SOH estable en este MVP
            error_code=None if i < count - 2 else "WARN_TEMP_HIGH"
        )
        TELEMETRY_DATA.append(record)

    return TELEMETRY_DATA


@app.get("/telemetry/latest", response_model=List[TelemetryRecord])
def get_latest_telemetry(limit: int = 5):
    """
    Devuelve los últimos N registros de telemetría en memoria.
    """
    if not TELEMETRY_DATA:
        return []

    return TELEMETRY_DATA[-limit:]
