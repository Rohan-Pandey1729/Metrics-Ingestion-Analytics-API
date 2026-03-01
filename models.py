from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from database import Base

class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(String, index=True)
    metric_type = Column(String, index=True) # cpu, memory, latency
    value = Column(Float) # percentage for cpu/memory, ms for latency
    timestamp = Column(DateTime(timezone=True), server_default=func.now()) # auto-set to current time on insert

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(String, index=True)
    metric_type = Column(String)
    value = Column(Float)
    threshold = Column(Float)
    message = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
