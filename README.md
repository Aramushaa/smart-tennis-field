# Smart Tennis Field — Thesis

V 0.1

Python microservices for Smart Tennis Field (MQTT + FastAPI + Postgres).

## Phase 0 — MQTT Quickstart ✅

- EMQX broker running in Docker (`docker run -p 2883:1883 -p 28083:18083 emqx:latest`).
- Publisher (`publisher_live.py`) sends JSON payloads every 2s.
- Subscriber (`subscriber_live.py`) listens on topic `tennis/sensor/1/events`.
- Connections confirmed via EMQX Dashboard (port 28083).
