from datetime import datetime
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.db import Base, engine, get_db
from backend.models import Telemetry
from backend.schemas import TelemetryIn, IngestResponse, LatestResponse, SummaryResponse
from backend import services

app = FastAPI(title="Battery & Vehicle Monitoring API", version="0.1.0")


@app.on_event("startup")
def startup():
    # crea tablas
    Base.metadata.create_all(bind=engine)

    # habilita timescaledb si está (no truena si ya existe)
    try:
        with engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb;"))
            # convertir a hypertable (si existe función y no está ya)
            conn.execute(
                text(
                    "SELECT create_hypertable('telemetry', 'ts', if_not_exists => TRUE);"
                )
            )
    except Exception:
        # si no está disponible timescale, no pasa nada para el MVP
        pass


@app.get("/api/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "OK", "db": "OK"}


# ------------------------------------------------------------
# Ingest telemetry
# - Endpoint "nuevo":  POST /api/telemetry
# - Endpoint "compat": POST /api/telemetry/ingest  (lo usa demo.sh)
# ------------------------------------------------------------
@app.post("/api/telemetry", response_model=IngestResponse)
@app.post("/api/telemetry/ingest", response_model=IngestResponse)
def ingest_telemetry(items: List[TelemetryIn], db: Session = Depends(get_db)):
    if not items:
        raise HTTPException(status_code=400, detail="Lista vacía")

    rows = [Telemetry(**it.model_dump()) for it in items]
    inserted = services.ingest(db, rows)
    return {"inserted": inserted}


def _latest_for_vin(vin: str, db: Session) -> LatestResponse:
    row = services.get_latest(db, vin)
    if row is None:
        raise HTTPException(status_code=404, detail="Sin telemetría para este VIN")

    power_kw = services.compute_power_kw(row.pack_voltage, row.pack_current)
    alerts = services.compute_alerts(row)

    return LatestResponse(
        vin=row.vin,
        ts=row.ts,
        soc=row.soc,
        soh=row.soh,
        pack_voltage=row.pack_voltage,
        pack_current=row.pack_current,
        power_kw=power_kw,
        max_temp=row.max_temp,
        min_temp=row.min_temp,
        odo_km=row.odo_km,
        alerts=alerts,
    )


# ------------------------------------------------------------
# Latest telemetry
# - Endpoint "nuevo":  GET /api/vehicles/{vin}/latest
# - Endpoint "compat": GET /api/telemetry/latest?vin=...
# ------------------------------------------------------------
@app.get("/api/vehicles/{vin}/latest", response_model=LatestResponse)
def latest_vehicle(vin: str, db: Session = Depends(get_db)):
    return _latest_for_vin(vin, db)


@app.get("/api/telemetry/latest", response_model=LatestResponse)
def latest_compat(vin: str = Query(...), db: Session = Depends(get_db)):
    return _latest_for_vin(vin, db)


def _summary_for_vin(vin: str, from_ts: datetime, to_ts: datetime, db: Session) -> SummaryResponse:
    if to_ts <= from_ts:
        raise HTTPException(status_code=400, detail="to_ts debe ser mayor que from_ts")

    samples, soc_min, soc_max, temp_max, temp_min = services.get_summary(
        db, vin, from_ts, to_ts
    )

    return SummaryResponse(
        vin=vin,
        from_ts=from_ts,
        to_ts=to_ts,
        samples=samples,
        soc_min=soc_min,
        soc_max=soc_max,
        temp_max=temp_max,
        temp_min=temp_min,
    )


# ------------------------------------------------------------
# Summary telemetry
# - Endpoint "nuevo":  GET /api/vehicles/{vin}/summary?from_ts=...&to_ts=...
# - Endpoint "compat": GET /api/telemetry/summary?vin=...&from_ts=...&to_ts=...
# ------------------------------------------------------------
@app.get("/api/vehicles/{vin}/summary", response_model=SummaryResponse)
def summary_vehicle(vin: str, from_ts: datetime, to_ts: datetime, db: Session = Depends(get_db)):
    return _summary_for_vin(vin, from_ts, to_ts, db)


@app.get("/api/telemetry/summary", response_model=SummaryResponse)
def summary_compat(
    vin: str = Query(...),
    from_ts: datetime = Query(...),
    to_ts: datetime = Query(...),
    db: Session = Depends(get_db),
):
    return _summary_for_vin(vin, from_ts, to_ts, db)
