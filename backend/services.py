from typing import List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from .models import Telemetry
from .schemas import Alert

# Reglas MVP (demo)
TEMP_RED = 60.0
TEMP_YELLOW = 50.0
SOC_RED = 10.0
SOC_YELLOW = 20.0

def compute_power_kw(v: Optional[float], a: Optional[float]) -> Optional[float]:
    if v is None or a is None:
        return None
    return round((v * a) / 1000.0, 4)

def compute_alerts(row: Telemetry) -> List[Alert]:
    alerts: List[Alert] = []

    tmax = row.max_temp
    if tmax is not None:
        if tmax >= TEMP_RED:
            alerts.append(Alert(code="HIGH_TEMP", severity="RED",
                                message=f"Temp alta: {tmax:.1f}°C (>= {TEMP_RED}°C)"))
        elif tmax >= TEMP_YELLOW:
            alerts.append(Alert(code="TEMP_WARNING", severity="YELLOW",
                                message=f"Temp elevada: {tmax:.1f}°C (>= {TEMP_YELLOW}°C)"))

    soc = row.soc
    if soc is not None:
        if soc <= SOC_RED:
            alerts.append(Alert(code="LOW_SOC", severity="RED",
                                message=f"SOC crítico: {soc:.1f}% (<= {SOC_RED}%)"))
        elif soc <= SOC_YELLOW:
            alerts.append(Alert(code="SOC_WARNING", severity="YELLOW",
                                message=f"SOC bajo: {soc:.1f}% (<= {SOC_YELLOW}%)"))

    soh = row.soh
    if soh is not None and soh < 80:
        alerts.append(Alert(code="SOH_DEGRADED", severity="YELLOW",
                            message=f"SOH degradado: {soh:.1f}% (< 80%)"))

    return alerts

def ingest(db: Session, items: List[Telemetry]) -> int:
    db.add_all(items)
    db.commit()
    return len(items)

def get_latest(db: Session, vin: str) -> Optional[Telemetry]:
    stmt = select(Telemetry).where(Telemetry.vin == vin).order_by(Telemetry.ts.desc()).limit(1)
    return db.execute(stmt).scalars().first()

def get_summary(db: Session, vin: str, from_ts: datetime, to_ts: datetime) -> Tuple[int, Optional[float], Optional[float], Optional[float], Optional[float]]:
    stmt = (
        select(
            func.count(Telemetry.id),
            func.min(Telemetry.soc),
            func.max(Telemetry.soc),
            func.max(Telemetry.max_temp),
            func.min(Telemetry.min_temp),
        )
        .where(Telemetry.vin == vin)
        .where(Telemetry.ts >= from_ts)
        .where(Telemetry.ts <= to_ts)
    )
    c, soc_min, soc_max, temp_max, temp_min = db.execute(stmt).one()
    return int(c), soc_min, soc_max, temp_max, temp_min
