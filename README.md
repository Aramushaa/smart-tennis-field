# Smart Tennis Field — Thesis

V 0.1

Python microservices for Smart Tennis Field (MQTT + FastAPI + Postgres).

## Phase 0 — MQTT Quickstart ✅

- EMQX broker running in Docker (`docker run -p 2883:1883 -p 28083:18083 emqx:latest`).
- Publisher (`publisher_live.py`) sends JSON payloads every 2s.
- Subscriber (`subscriber_live.py`) listens on topic `tennis/sensor/1/events`.
- Connections confirmed via EMQX Dashboard (port 28083).

### Run EMQX (Phase 0)
```bash
docker run -d --name emqx -p 2883:1883 -p 28083:18083 emqx:latest

username: admin
password: public


### Run FastAPI with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000

http://localhost:8000/docs

http://localhost:8000/health

### Publish a message (easy test)

In Swagger: POST /publish with body:

{
  "topic": "tennis/hello",
  "payload": { "msg": "yo", "ts": 123 }
}
