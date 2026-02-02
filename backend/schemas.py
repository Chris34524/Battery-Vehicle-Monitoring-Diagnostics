from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class TelemetryIn(BaseModel):
    vin: str = Field(min_length=5, max_length=40)
    ts: datetime

    soc: Optional[float] = Field(default=None, ge=0, le=100)
    soh: Optional[float] = Field(default=None, ge=0, le=100)
    pack_voltage: Optional[float] = None
    pack_current: Optional[float] = None
    max_temp: Optional[float] = None
    min_temp: Optional[float] = None
    odo_km: Optional[float] = None

class IngestResponse(BaseModel):
    inserted: int

class Alert(BaseModel):
    code: str
    severity: str  # GREEN/YELLOW/RED
    message: str

class LatestResponse(BaseModel):
    vin: str
    ts: datetime
    soc: Optional[float] = None
    soh: Optional[float] = None
    pack_voltage: Optional[float] = None
    pack_current: Optional[float] = None
    power_kw: Optional[float] = None
    max_temp: Optional[float] = None
    min_temp: Optional[float] = None
    odo_km: Optional[float] = None
    alerts: List[Alert] = []

class SummaryResponse(BaseModel):
    vin: str
    from_ts: datetime
    to_ts: datetime
    samples: int
    soc_min: Optional[float] = None
    soc_max: Optional[float] = None
    temp_max: Optional[float] = None
    temp_min: Optional[float] = None
