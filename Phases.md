📘 phases.md — Smart Tennis Field (Master Thesis) Roadmap

This file defines the system evolution from MVP → Thesis-grade distributed system.

Each phase contains:

🎯 Goal

📦 Deliverables

✅ Definition of Done

🧠 Engineering Notes

Phase 0 — MQTT Infrastructure (✅ Done)
🎯 Goal

Validate reliable end-to-end event transport over MQTT.

📦 Deliverables

EMQX broker (Dockerized)

Dummy publisher → tennis/sensor/1/events

Subscriber confirming message receipt

Topic naming convention defined

JSON payload schema defined

✅ Definition of Done

Publisher → broker → subscriber verified

QoS behavior understood

Payload structure documented

🧠 Notes

This phase validates messaging reliability before persistence.

MQTT chosen for lightweight event-driven architecture.

Phase 1 — Ingest Service + Persistence (✅ Done)
🎯 Goal

Transform MQTT events into durable, queryable time-series data.

📦 Deliverables

FastAPI ingest microservice

MQTT client lifecycle managed via FastAPI lifespan

Event normalization envelope:

{
  "topic": "...",
  "ts": "...",
  "payload": {...}
}


In-memory ring buffer (debug window)

InfluxDB 3 Core persistence

Time-range query endpoints:

GET /events?limit=N

GET /events?from=...&to=...&limit=N

Docker Compose deployment

Token generation workflow documented

✅ Definition of Done

MQTT events written to InfluxDB 3

Data persists across service restarts

Time-range queries return correct data

Token-based authentication verified

🧠 Notes

InfluxDB 3 Core requires Bearer token.

Line protocol used for write efficiency.

Tags: stream, source_id

Field: payload (JSON string)

Phase 2 — Real Producers (Edge Gateways)
🎯 Goal

Replace simulated data with real edge gateways.

2A — Vision Gateway (YOLO)
📦 Deliverables

vision-gateway service

Reads RTSP / USB / video file

YOLO-based ball detection

Basic tracking (ID + trajectory)

Publishes:

tennis/camera/<id>/ball

✅ Definition of Done

Ball detections appear in InfluxDB

Stable publish rate

Frame processing latency measured

2B — Sensor Gateway (ST AIoT Craft)
📦 Deliverables

sensor-gateway

Reads ST AIoT Craft output (BLE/UART/etc.)

Publishes:

tennis/sensor/<id>/events

✅ Definition of Done

Sensor data stored in DB

Timestamp synchronization validated

🧠 Engineering Notes

Gateways publish only.

They never access database directly.

All persistence flows through ingest service.

Time synchronization strategy must be defined:

edge timestamp vs server timestamp

Phase 3 — Rules Engine (Tennis Semantics)
🎯 Goal

Convert raw telemetry into tennis events.

📦 Deliverables

rules-engine microservice

Correlates:

sensor events

ball trajectory

Detects:

bounce

serve_ok / serve_fault

out

Publishes:

tennis/alerts/<type>

✅ Definition of Done

Deterministic rule evaluation

Reproducible alert generation

Alerts stored in DB

🧠 Notes

This is where the project becomes academically interesting:

Multi-stream correlation

Time window alignment

False positive control

Phase 4 — Control Unit (System Orchestration)
🎯 Goal

Introduce system-level state and control plane.

📦 Deliverables

control-unit service

Match states:

idle

warmup

match

maintenance

Publishes:

tennis/cmd/<target>


Heartbeat monitoring:

tennis/system/heartbeat/<node>

✅ Definition of Done

System behavior changes based on mode

Services respond to commands

🧠 Notes

This introduces:

Distributed coordination

Operational robustness

Phase 5 — Visualization Layer
🎯 Goal

Make the system observable.

5A — Grafana MVP (Recommended First)
📦 Deliverables

InfluxDB datasource

Panels:

events/min

stream breakdown

alert rate

time-series view

✅ Definition of Done

Real-time ingestion visible

Historical exploration possible

5B — Custom Web UI (Optional Advanced)

React/Next.js dashboard

Live feed via WebSocket

Event replay

Phase 6 — Highlight Clipper (Optional Advanced Feature)
🎯 Goal

Auto-generate match highlights.

📦 Deliverables

video-clipper

Subscribes to:

tennis/alerts/<type>


Clips ±N seconds

Uploads to S3/MinIO

Publishes:

tennis/clip_created

✅ Definition of Done

Alert → clip → playable URL

Clip metadata stored

Phase 7 — Config + Service Registry
🎯 Goal

Improve scalability and maintainability.

Deliverables

config-service

Centralized rule parameters

catalog-service for service discovery

Definition of Done

Rules adjustable without redeploy

Dynamic service registration

Phase 8 — Security Layer
🎯 Goal

Secure distributed services.

Deliverables

JWT authentication

Role-based access

Optional MQTT ACL

Secure REST endpoints

Definition of Done

Unauthorized requests rejected

Roles enforced

Phase 9 — Thesis Evaluation & Validation
🎯 Goal

Produce thesis-grade measurable results.

Deliverables
System Evaluation

End-to-end latency

Throughput under load

Packet loss behavior

CPU/GPU usage (YOLO)

Reliability Tests

Service restart recovery

Broker restart behavior

DB reconnection logic

Documentation

Architecture diagrams

Event schema specification

Deployment guide (Docker Compose)

Limitations & future work

Definition of Done

Fully reproducible demo

Measured performance metrics

Academic documentation ready