from pydantic import BaseModel, field_validator, model_validator
from datetime import datetime
from typing import Optional

VALID_METRIC_TYPES = {"cpu", "memory", "latency"}
VALUE_RANGES = {
    "cpu": (0, 100),
    "memory": (0, 100),
    "latency": (0, 10000),
}

class MetricCreate(BaseModel):
    server_id: str
    metric_type: str
    value: float
    timestamp: Optional[datetime] = None

    @field_validator('metric_type')
    @classmethod
    def validate_metric_type(cls, v):
        if v not in VALID_METRIC_TYPES:
            raise ValueError(f'metric_type must be one of {VALID_METRIC_TYPES}')
        return v

    @model_validator(mode='after')
    def validate_value_range(self):
        if self.metric_type in VALUE_RANGES:
            min_val, max_val = VALUE_RANGES[self.metric_type]
            if not (min_val <= self.value <= max_val):
                raise ValueError(f'{self.metric_type} value must be between {min_val} and {max_val}')
        return self

class Metric(BaseModel):
    id: int
    server_id: str
    metric_type: str
    value: float
    timestamp: Optional[datetime] = None

    model_config = {"from_attributes": True}

class Alert(BaseModel):
    id: int
    server_id: str
    metric_type: str
    value: float
    threshold: float
    message: str
    timestamp: Optional[datetime] = None

    model_config = {"from_attributes": True}

class ServerStats(BaseModel):
    server_id: str
    metric_type: str
    average: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None