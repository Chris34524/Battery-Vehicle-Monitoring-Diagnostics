from sqlalchemy import Column, BigInteger, Float, String, DateTime, Index
from sqlalchemy.sql import func
from .db import Base

class Telemetry(Base):
    __tablename__ = "telemetry"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    vin = Column(String(40), nullable=False, index=True)

    ts = Column(DateTime(timezone=True), nullable=False, index=True)

    # BMS / pack (MVP)
    soc = Column(Float, nullable=True)          # %
    soh = Column(Float, nullable=True)          # %
    pack_voltage = Column(Float, nullable=True) # V
    pack_current = Column(Float, nullable=True) # A
    max_temp = Column(Float, nullable=True)     # °C
    min_temp = Column(Float, nullable=True)     # °C

    odo_km = Column(Float, nullable=True)       # km
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

Index("ix_telemetry_vin_ts", Telemetry.vin, Telemetry.ts.desc())
