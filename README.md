# 🎾 Smart Tennis Field — Thesis

Version: 0.2 (Phase 1 – In Progress)

A Python-based Smart Tennis Field backend using MQTT + FastAPI, designed for real-time ingestion of sensor and camera events, with a scalable persistence layer.

This project is developed as a thesis / research prototype, following a phased, engineering-driven architecture.

## 🧱 Architecture Overview

- Sensors / Cameras → publish events via MQTT
- MQTT Broker (EMQX) → central event bus
- Ingest Service (FastAPI):
  - subscribes to MQTT topics
  - normalizes and validates events
  - stores events (in-memory → database)
  - exposes REST APIs for inspection and dashboards
- Time-Series Database: InfluxDB 3 (planned / optional)

## ✅ Phase 0 — MQTT Quickstart (Completed)

Goal: verify end-to-end MQTT communication.

What’s implemented

- EMQX broker running in Docker
- Dummy publisher sends JSON events
- Subscriber receives events on tennis topics
- Connectivity verified via EMQX Dashboard

### Run EMQX

```bash
docker run -d --name emqx \
  -p 2883:1883 \
  -p 28083:18083 \
  emqx:latest
```

### Dashboard

- URL: http://localhost:28083
- Username: admin
- Password: public

### Publisher (Fake Sensor)

`publisher_live.py`

- Publishes JSON payloads every 2 seconds
- Topic: `tennis/sensor/1/events`
- Used for testing without real hardware

### Subscriber (Debug Listener)

`subscriber_live.py`

- Subscribes to the same topic
- Prints incoming messages to terminal
- Used to verify broker + topics

## 🚧 Phase 1 — Data Ingestion Service (In Progress)

Goal: turn MQTT messages into structured, queryable data.

What’s implemented so far

- FastAPI ingest service (`main.py`)
- MQTT client runs in background thread using lifespan lifecycle
- Incoming MQTT messages are:
  - decoded
  - normalized into a standard event envelope
  - stored in an in-memory ring buffer
- REST API to inspect received events

### Run the Ingest Service

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Available Endpoints

- Swagger UI: http://localhost:8000/docs
- Health check: `GET /health`
- View received events (debug window): `GET /events?limit=50`
- Publish MQTT message via HTTP (test helper): `POST /publish`

Example body:

```json
{
  "topic": "tennis/hello",
  "payload": { "msg": "yo", "ts": 123 }
}
```

## 🧠 Event Model (Current MVP)

All incoming data is normalized into a standard structure:

```json
{
  "ts": "ISO-8601 timestamp",
  "topic": "mqtt/topic",
  "source": "mqtt",
  "payload": { "...original data..." }
}
```

This envelope ensures consistency across:

- sensors
- cameras
- future analytics and storage layers

## 🧪 In-Memory Event Buffer (Phase 1 – Step 1)

- Stores the last N events (default: 100)
- Used for:
  - debugging
  - verifying ingestion
  - early dashboard development
- Acts as a fast-feedback window before database persistence

## 🧊 InfluxDB 3 (Planned / Optional)

InfluxDB 3 Core is selected as the time-series persistence layer.

Quickstart (Local)

```bash
docker pull influxdb:3-core

docker run -it --name influxdb3 \
  -p 8181:8181 \
  -v ~/.influxdb3_data:/.data \
  influxdb:3-core influxdb3
```

InfluxDB integration is feature-flagged and will be enabled once tokens and schema are finalized.

## 🗺️ Roadmap

Phase 1 (Current)

- ✅ MQTT ingestion
- ✅ Event normalization
- ✅ In-memory event buffer
- ⏳ InfluxDB 3 persistence
- ⏳ Time-range queries (`/events?from=&to=`)

Phase 2 (Next)

- Rules engine (serve / bounce / out detection)
- Camera + sensor correlation
- Alerts via MQTT

Phase 3 (Future)

- Video clip generation
- Dashboard (Grafana / Web UI)
- Full thesis evaluation

## 🧑‍🔬 Notes

- Built with Python 3.11
- Designed for IoT + real-time sports analytics
- Architecture favors clarity, debuggability, and scalability
