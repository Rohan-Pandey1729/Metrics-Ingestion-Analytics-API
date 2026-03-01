from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
import pytest
from sqlalchemy.pool import StaticPool

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool  # forces all connections to share same in-memory DB
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# --- Tests ---

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_metric_valid():
    response = client.post("/metrics", json={
        "server_id": "server-1",
        "metric_type": "cpu",
        "value": 50.0
    })
    assert response.status_code == 201
    assert response.json()["server_id"] == "server-1"
    assert response.json()["value"] == 50.0

def test_alert_created_on_threshold_exceeded():
    client.post("/metrics", json={
        "server_id": "server-1",
        "metric_type": "cpu",
        "value": 95.0
    })
    response = client.get("/alerts/server-1")
    assert response.status_code == 200
    alerts = response.json()
    assert any(a["metric_type"] == "cpu" and a["value"] == 95.0 for a in alerts)

def test_get_metrics_not_found():
    response = client.get("/metrics/nonexistent-server")
    assert response.status_code == 404

def test_summary_average():
    client.post("/metrics", json={"server_id": "srv", "metric_type": "cpu", "value": 40.0})
    client.post("/metrics", json={"server_id": "srv", "metric_type": "cpu", "value": 60.0})
    response = client.get("/metrics/srv/summary")
    assert response.status_code == 200
    cpu = next(i for i in response.json() if i["metric_type"] == "cpu")
    assert cpu["average"] == 50.0
    assert cpu["min"] == 40.0
    assert cpu["max"] == 60.0