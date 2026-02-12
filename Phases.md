# phases.md — Smart Tennis Field (Thesis) Roadmap

This file defines the project phases from MVP → full thesis demo.
Each phase has: **Goal**, **Deliverables**, **Definition of Done**, and **Notes**.

---

## Phase 0 — MQTT Infrastructure (✅ Done)
### Goal
Prove end-to-end message transport over MQTT.

### Deliverables
- EMQX broker in Docker
- Dummy publisher (`publisher_live.py`) → `tennis/sensor/1/events`
- Subscriber (`subscriber_live.py`) prints messages
- Broker connectivity verified (Dashboard + logs)

### Definition of Done
- Publisher → broker → subscriber confirmed
- Topics and payloads are consistent JSON

---

## Phase 1 — Ingest Service + Persistence (✅ Done)
### Goal
Turn MQTT events into **stored, queryable data**.

### Deliverables
- FastAPI ingest service (`main.py`)
- MQTT client lifecycle managed with FastAPI lifespan
- Event normalization envelope
- In-memory buffer (last N)
- InfluxDB 3 Core persistence (write on ingest)
- Query endpoint:
  - `GET /events?limit=...`
  - `GET /events?from=...&to=...&limit=...` (Influx-backed)
- Token setup workflow documented

### Definition of Done
- MQTT events are written to InfluxDB 3
- Data survives FastAPI restarts
- `/events` returns correct data for time ranges

### Notes
- InfluxDB 3 Core requires Bearer token for HTTP access and queries.

---

## Phase 2 — Real Producers (Edge Gateways) (Next)
### Goal
Replace dummy data with real sensor + camera producers that publish into MQTT.

### Deliverables
**2A — Vision Gateway (YOLO)**
- `vision-gateway` service:
  - reads RTSP/USB/video file
  - runs ball detection/tracking (YOLO + tracking)
  - publishes:
    - `tennis/camera/<id>/ball`

**2B — Sensor Gateway (ST AIoT Craft output)**
- `sensor-gateway` service:
  - connects to ST sensor output (BLE/UART/I²C)
  - reads motion class + confidence
  - publishes:
    - `tennis/sensor/<id>/events`

**Ingest updates**
- Subscribe to both:
  - `tennis/sensor/+/events`
  - `tennis/camera/+/ball`

### Definition of Done
- Ball stream + sensor stream both appear in InfluxDB
- Consistent event schema + timestamps across both producers
- Stable publish rate (no flooding)

### Notes
- AIoT Craft is mostly “on-device”; Python reads the results and publishes.
- YOLO runs in Python gateway (not inside ingest).

---

## Phase 3 — Rules Engine (Tennis Logic)
### Goal
Convert raw events into **tennis semantics** (serve/bounce/out/etc.).

### Deliverables
- `rules-engine` microservice:
  - subscribes to sensor + camera topics
  - correlates time windows
  - detects:
    - bounce event (trajectory/velocity change)
    - serve_ok / serve_fault (impact + bounce in service box)
    - out detection (bounce outside court polygon)
- Publishes alerts:
  - `tennis/alerts/<type>`
- Stores alerts into DB (via ingest or direct write)

### Definition of Done
- Alerts produced reliably with repeatable test sequences
- Alerts persisted and queryable

---

## Phase 4 — Control Unit (Orchestration)
### Goal
Add match “state” and a control plane for the system.

### Deliverables
- `control-unit` microservice:
  - modes: `idle | warmup | match | maintenance`
  - publishes commands:
    - `tennis/cmd/<target>`
  - monitors heartbeats:
    - `tennis/system/heartbeat/<node>`
- REST endpoints for mode switching
- Basic safety rules (ignore events outside match mode, etc.)

### Definition of Done
- System behavior changes based on mode
- Commands reach target services reliably

---

## Phase 5 — Dashboard (Visualization)
### Goal
Make the system visible to humans (live + history).

### Deliverables
**5A — Grafana MVP (recommended first)**
- Grafana datasource connected to InfluxDB 3
- Panels:
  - events per minute
  - event type breakdown
  - alerts count
  - last events table
  - (later) trajectory views (if supported or via custom panel)

**5B — Custom Web UI (optional)**
- React/Next.js dashboard
- Live feed (WebSocket or MQTT-over-WebSocket)
- History via REST queries

### Definition of Done
- Live ingestion can be observed
- Historical queries work in UI
- At least one end-to-end demo dashboard exists

---

## Phase 6 — Video Clipper + Object Storage (Optional Highlight System)
### Goal
Auto-generate highlight clips around important events.

### Deliverables
- `video-clipper` service:
  - subscribes to `tennis/alerts/<type>`
  - clips ±N seconds around event (FFmpeg)
  - uploads to MinIO/S3
  - publishes:
    - `tennis/clip_created`
- Metadata stored and served to dashboard

### Definition of Done
- Alert → clip created → clip viewable
- Clips linked to events/alerts

---

## Phase 7 — Config Service + Catalog (Scalability / Maintainability)
### Goal
Centralize configuration and service discovery.

### Deliverables
- `config-service`:
  - rules/config in DB
  - publishes `config/updated`
- `catalog-service` (registry):
  - register services
  - query endpoints for discovery

### Definition of Done
- Rules and configs can change without redeploy
- Services discover each other dynamically

---

## Phase 8 — Security Layer (JWT/OIDC + Optional MQTT ACL)
### Goal
Secure APIs and optionally MQTT.

### Deliverables
- Keycloak OIDC
- JWT verification in FastAPI services (JWKS)
- Role-based access control (coach/admin)
- Optional MQTT auth/ACL (if broker supports)

### Definition of Done
- Protected REST endpoints
- Valid tokens required
- Roles enforced

---

## Phase 9 — Thesis Integration + Evaluation
### Goal
Finalize thesis-grade results with measurements and documentation.

### Deliverables
- Full end-to-end demo:
  - sensor/camera → ingest → rules → alerts → dashboard (→ clips optional)
- Performance evaluation:
  - latency, throughput, loss rate, CPU load
- Reliability tests:
  - disconnect/reconnect
  - backpressure behavior
- Documentation:
  - architecture diagrams
  - event schema spec
  - deployment guide (Docker Compose)

### Definition of Done
- Reproducible demo setup
- Measured results reported in thesis format
- Clean repo documentation + final deliverables

---

## Appendix — Recommended Phase Order (Practical)
1. Phase 0 ✅
2. Phase 1 ✅
3. Phase 2 (YOLO gateway first, then sensor gateway)
4. Phase 3 (rules engine)
5. Phase 5A (Grafana MVP) — can be done right after Phase 2 or 3
6. Phase 4 (control unit)
7. Phase 6 (clipper) optional
8. Phase 7 + 8 (config + security)
9. Phase 9 (evaluation + thesis write-up)
