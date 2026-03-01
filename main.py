from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import models, schemas
from database import SessionLocal, engine, get_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Metrics Ingestion & Analytics API")

# Threshold Constants
METRIC_THRESHOLDS = {
    "cpu": 90.0,
    "memory": 85.0,
    "latency": 2000.0,
}

@app.get("/health")
def health_check():
    logger.info("Health check called")
    return {"status": "ok"}

@app.post("/metrics", response_model=schemas.Metric, status_code=201)
def create_metric(metric: schemas.MetricCreate, db: Session = Depends(get_db)):
    # 1. Save to metrics table
    db_metric = models.Metric(
        server_id=metric.server_id,
        metric_type=metric.metric_type,
        value=metric.value,
        **({"timestamp": metric.timestamp} if metric.timestamp else {})
    )
    db.add(db_metric)
    logger.info(f"Metric ingested: {metric.metric_type} = {metric.value} for server {metric.server_id}")

    # 2. Check threshold
    threshold = METRIC_THRESHOLDS.get(metric.metric_type)
    if threshold is not None and metric.value > threshold:
        # 3. Create alert if exceeded
        alert_msg = f"{metric.metric_type.upper()} usage exceeded threshold {threshold}: {metric.value}"
        db_alert = models.Alert(
            server_id=metric.server_id,
            metric_type=metric.metric_type,
            value=metric.value,
            threshold=threshold,
            message=alert_msg,
            **({"timestamp": metric.timestamp} if metric.timestamp else {})
        )
        db.add(db_alert)
        logger.info(f"ALERT: {alert_msg} for server {metric.server_id}")
        

    db.commit()
    db.refresh(db_metric)
    return db_metric

@app.get("/metrics/{server_id}", response_model=List[schemas.Metric])
def get_metrics(server_id: str, db: Session = Depends(get_db)):
    metrics = db.query(models.Metric).filter(models.Metric.server_id == server_id).all()
    if not metrics:
        raise HTTPException(status_code=404, detail="Server not found")
    return metrics

@app.get("/alerts/{server_id}", response_model=List[schemas.Alert])
def get_alerts(server_id: str, db: Session = Depends(get_db)):
    alerts = db.query(models.Alert).filter(models.Alert.server_id == server_id).all()
    if not alerts:
        raise HTTPException(status_code=404, detail=f"No alerts found for server {server_id}")
    return alerts

@app.get("/metrics/{server_id}/summary", response_model=List[schemas.ServerStats])
def get_metric_summary(server_id: str, db: Session = Depends(get_db)):
    # Calculate average, min, and max for each metric type for the given server
    stats = db.query(
        models.Metric.metric_type,
        func.avg(models.Metric.value).label("average"),
        func.min(models.Metric.value).label("min"),
        func.max(models.Metric.value).label("max")
    ).filter(
        models.Metric.server_id == server_id
    ).group_by(
        models.Metric.metric_type
    ).all()

    if not stats:
        raise HTTPException(status_code=404, detail=f"No metrics found for server {server_id}")

    # Convert the query results to a list of ServerStats objects
    summary = []
    for stat in stats:
        summary.append(schemas.ServerStats(
            server_id=server_id,
            metric_type=stat.metric_type,
            average=stat.average,
            min=stat.min,
            max=stat.max
        ))
    
    return summary
