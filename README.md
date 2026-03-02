# Metrics Ingestion & Analytics API

A REST API for ingesting, storing, and analyzing server performance metrics. Built with FastAPI and SQLAlchemy, it supports real-time threshold alerting and per-server statistical summaries.

## Features

- **Metric ingestion** — ingest CPU, memory, and latency readings for any server
- **Automatic alerting** — alerts are automatically created when a metric exceeds a configured threshold
- **Analytics summaries** — query per-server, per-metric-type averages, minimums, and maximums
- **Input validation** — metric types and value ranges are validated on ingestion
- **Dual database support** — SQLite for local development, PostgreSQL for production
- **Dockerized** — ships with a `Dockerfile` for containerized deployment
- **CI** — GitHub Actions runs the test suite on every push and pull request

## Tech Stack

- **FastAPI** — API framework
- **SQLAlchemy** — ORM and database abstraction
- **Pydantic v2** — request/response validation and serialization
- **SQLite / PostgreSQL** — persistence layer
- **Uvicorn** — ASGI server
- **Pytest** — test suite

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/metrics` | Ingest a new metric reading |
| `GET` | `/metrics/{server_id}` | Retrieve all metrics for a server |
| `GET` | `/metrics/{server_id}/summary` | Get avg/min/max per metric type for a server |
| `GET` | `/alerts/{server_id}` | Retrieve all alerts triggered for a server |

## Metric Types & Thresholds

| Metric | Unit | Alert Threshold |
|--------|------|-----------------|
| `cpu` | % (0–100) | > 90% |
| `memory` | % (0–100) | > 85% |
| `latency` | ms (0–10,000) | > 2,000 ms |

When an ingested value exceeds its threshold, an alert record is automatically created alongside the metric.

## Getting Started

### Local (without Docker)

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs are at `http://localhost:8000/docs`.

### With Docker

```bash
docker build -t metrics-api .
docker run -p 8000:8000 metrics-api
```

### PostgreSQL (production)

Set the `DATABASE_URL` environment variable before starting the server:

```bash
export DATABASE_URL="postgresql://user:password@host:5432/dbname"
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Example Usage

**Ingest a metric:**
```bash
curl -X POST http://localhost:8000/metrics \
  -H "Content-Type: application/json" \
  -d '{"server_id": "web-01", "metric_type": "cpu", "value": 95.0}'
```

**Get a server summary:**
```bash
curl http://localhost:8000/metrics/web-01/summary
```

**Check alerts:**
```bash
curl http://localhost:8000/alerts/web-01
```

## Running Tests

```bash
pytest
```

Tests use an in-memory SQLite database and are fully isolated — no external dependencies required.
