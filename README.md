# 🎾 Smart Tennis Field — Thesis

Version: 0.4
Status: Phase 1 Completed — Ingestion + Persistence + Retrieval

A Python-based Smart Tennis Field backend using:

- MQTT (event bus)
- FastAPI (microservice layer)
- InfluxDB 3 Core (time-series persistence)

Designed for real-time ingestion, storage, and querying of tennis sensor and camera events.

## 🧱 Architecture Overview (Current System)

Sensor / Camera
        ↓
      MQTT (EMQX)
        ↓
  Ingest Service (FastAPI)
        ↓
   InfluxDB 3 Core
        ↓
   REST Query API

## ✅ Phase 0 — MQTT Infrastructure (Completed)

Goal: Verify event transport layer.

Implemented

- EMQX broker in Docker
- Publisher script (`publisher_live.py`)
- Subscriber script (`subscriber_live.py`)
- Verified via EMQX dashboard

### Run EMQX

```bash
docker run -d --name emqx \
  -p 1883:1883 \
  -p 18083:18083 \
  emqx:latest
```

### Dashboard

- http://localhost:18083
- user: admin
- pass: public

## ✅ Phase 1 — Ingestion + Persistence (Completed)

Goal: Convert MQTT messages into persistent, queryable data.

### Step 1 — Run InfluxDB 3 Core

```bash
docker pull influxdb:3-core

docker run -it --name influxdb3 \
  -p 8181:8181 \
  -v ~/.influxdb3_data:/.data \
  influxdb:3-core influxdb3
```

⚠️ If you delete the container, tokens must be recreated.

### Step 2 — Create Admin Token

```bash
curl -X POST http://localhost:8181/api/v3/configure/token/admin
```

Copy the `token` value.

### Step 3 — Test Token

```bash
curl http://localhost:8181/health \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Expected:

```json
{"status":"pass"}
```

### Step 4 — Configure FastAPI

Create `.env` file:

```bash
INFLUX_ENABLED=1
INFLUX_HOST=http://localhost:8181
INFLUX_TOKEN=your_token_here
INFLUX_DATABASE=tennis
INFLUX_TABLE=events
```

Add to `.gitignore`:

```
.env
```

Start FastAPI:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 5 — Run Publisher

```bash
python publisher_live.py
```

Verify:

- `GET /events?limit=10`
- `GET /events?source=influx&limit=10`
- No `[INFLUX] write error`

## 🧠 Event Model

Stored structure:

```json
{
  "time": "...",
  "topic": "...",
  "payload": "{original JSON string}"
}
```

Events can be queried with:

```bash
curl --get "http://localhost:8181/api/v3/query_sql" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --data-urlencode "db=tennis" \
  --data-urlencode "q=SELECT * FROM events LIMIT 10"
```

## ⚠️ Common Errors

MissingToken

- No Authorization header.

Fix:

- `-H "Authorization: Bearer TOKEN"`

InvalidToken

- Old token
- Deleted container
- Wrong header format

Fix:

- Recreate token
- Update `.env`
- Restart FastAPI

`/api/v2/write` errors

- Old v2 client writing to v3 server.

Fix:

- Use InfluxDB 3 client only.

## ✅ What Works Now

- Real-time MQTT ingestion
- Normalized event envelope
- In-memory debug buffer
- InfluxDB 3 persistence
- Time-range queries via `/events?from=&to=`
- SQL queries directly against Influx
- Restart-safe data storage

Phase 1 is complete.
