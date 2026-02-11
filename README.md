# 🎾 Smart Tennis Field — Thesis

Version: 0.3 (Phase 1 – Influx Persistence Working)

A Python-based Smart Tennis Field backend using MQTT + FastAPI + InfluxDB 3, designed for real-time ingestion of sensor and camera events with time-series persistence.

## 🧱 Architecture Overview

- Sensors / Cameras → publish events via MQTT
- MQTT Broker (EMQX) → central event bus
- Ingest Service (FastAPI):
  - subscribes to MQTT topics
  - normalizes and validates events
  - stores events (in-memory → InfluxDB 3)
  - exposes REST APIs
- Time-Series Database: InfluxDB 3 Core

## ✅ Phase 0 — MQTT Quickstart (Completed)

### Run EMQX

```bash
docker run -d --name emqx \
  -p 1883:1883 \
  -p 18083:18083 \
  emqx:latest
```

### Dashboard

- URL: http://localhost:18083
- Username: admin
- Password: public

## 🚧 Phase 1 — Ingest Service + Persistence (Working)

### Step 1 — Run InfluxDB 3 Core

⚠️ Important: If you remove the container, your token will change.

```bash
docker pull influxdb:3-core

docker run -it --name influxdb3 \
  -p 8181:8181 \
  -v ~/.influxdb3_data:/.data \
  influxdb:3-core influxdb3
```

### Step 2 — Create Admin Token (MANDATORY)

After Influx starts, open a new terminal:

```bash
curl -X POST http://localhost:8181/api/v3/configure/token/admin
```

Example output:

```json
{
  "id": 0,
  "name": "_admin",
  "token": "apiv3_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

🔑 Copy the value of `token`

You must use this token for:

- Health checks
- Writes
- Queries
- FastAPI environment variable

### Step 3 — Test Token

```bash
curl http://localhost:8181/health \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

If working:

```json
{"status":"pass"}
```

### Step 4 — Configure FastAPI to Use Influx

Before running uvicorn:

```bash
export INFLUX_ENABLED=1
export INFLUX_HOST=http://localhost:8181
export INFLUX_TOKEN=YOUR_TOKEN_HERE
export INFLUX_DATABASE=tennis
export INFLUX_TABLE=events
```

Now start FastAPI:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 5 — Run Publisher

```bash
python publisher_live.py
```

Now verify:

- GET http://localhost:8000/events?limit=10
- FastAPI logs show no `[INFLUX] write error`
- Influx logs show no `InvalidToken`

## 🧠 Why Token Changes

If you:

- Stop and remove container
- Run `docker rm influxdb3`
- Run a fresh container

Then InfluxDB creates a new catalog and previous token becomes invalid.

⚠️ In that case, you must re-run:

```bash
curl -X POST http://localhost:8181/api/v3/configure/token/admin
```

And update:

```bash
export INFLUX_TOKEN=NEW_TOKEN
```

## ⚠️ Common Errors & Fixes

❌ Error: MissingToken

`cannot authenticate token e=MissingToken`

Cause:

- No Authorization header sent

Fix:

- `-H "Authorization: Bearer YOUR_TOKEN"`

❌ Error: InvalidToken

`cannot authenticate token e=InvalidToken path="/api/v2/write"`

Cause:

- Wrong token
- Old token from deleted container
- Using v2 endpoint incorrectly

Fix:

- Generate new admin token
- Update `INFLUX_TOKEN`
- Restart FastAPI

❌ Error: Authorization header malformed

Cause:

- Wrong header format

Wrong:

- `-H "Authorization: YOUR_TOKEN"`

Correct:

- `-H "Authorization: Bearer YOUR_TOKEN"`

❌ Error: Writes failing silently

Check FastAPI logs:

`[INFLUX] write error: ...`

Most common cause:

- `INFLUX_ENABLED=1` but token not set
- Using wrong timestamp format

## 🔒 Security Notice

❗ Never commit your Influx token.

Create a `.env` file:

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

## ✅ What Works Now

- MQTT ingestion
- Event normalization
- In-memory debug buffer
- InfluxDB 3 persistence
- Token-based authentication

Manual SQL query via:

```bash
curl "http://localhost:8181/api/v3/query_sql?db=tennis" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"SELECT * FROM events LIMIT 10"}'
```

## 🗺️ Next Roadmap

Phase 1 Completion:

- Replace memory buffer query with Influx-backed query
- Implement `GET /events?from=...&to=...`

Phase 2:

- Rules engine
- Alert publishing
- Camera event support
