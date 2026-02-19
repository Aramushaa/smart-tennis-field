# Smart Tennis Field — IoT Event Pipeline (Docker Compose)

## Overview
This project implements a Smart Tennis Field architecture using:

- EMQX (MQTT broker)
- InfluxDB 3 Core (time-series database)
- FastAPI ingest service
- Sensor simulator (fake publisher)

All services run with Docker Compose.

## Architecture
```
Sensor Simulator -> EMQX (MQTT)
                     |
                     v
              Ingest Service
                     |
                     v
               InfluxDB 3 Core
                     |
                     v
                 REST API
```

## Quickstart (Docker Compose)

1. Start all services:
```bash
docker compose up -d --build
```

2. Create an admin token:
```bash
docker exec -it influxdb3 influxdb3 create token --admin
```

3. Put the token in `.env`:
```bash
INFLUX_TOKEN=YOUR_TOKEN
INFLUX_ENABLED=1
```

4. Restart the ingest service to reload `.env`:
```bash
docker compose restart ingest-service
```

## Endpoints

- EMQX dashboard: http://localhost:18083
- InfluxDB 3 Core: http://localhost:8181
- Ingest service API: http://localhost:8000

## API Routes

- `GET /health`
- `GET /events?limit=10`
- `POST /publish`

## MQTT Ports

- Host port: `2883`
- Container port: `1883`

If you connect from your host machine, use port `2883`.

## Stop Services

```bash
docker compose down
```

Do not use `docker compose down -v` unless you want to delete InfluxDB data and regenerate tokens.

## Project Structure

- `services/ingest_service/app/main.py`
- `services/ingest_service/app/mqtt.py`
- `services/ingest_service/app/influx.py`
- `services/ingest_service/app/config.py`
- `quickstarts/mqtt/Dockerfile.sensor`
- `docker-compose.yml`
- `.env`

## Troubleshooting

- EMQX fails to start due to port conflict:
  - Change `1883` to another host port in `docker-compose.yml` (e.g. `2883:1883`).
  - Update your host-side MQTT clients to match.

- InfluxDB auth errors:
  - Ensure `INFLUX_TOKEN` is set in `.env` and restart `ingest-service`.
  - If the volume was deleted, regenerate the admin token.

- Ingest service can’t connect to MQTT:
  - Confirm `emqx` container is running: `docker compose ps`.
  - Check logs: `docker compose logs emqx ingest-service`.

## Contributing

- Keep changes focused and scoped per commit.
- Prefer Docker Compose for local testing.
- Update `README.md` or `Phases.md` when behavior or workflow changes.

## Current Phase

- MQTT working
- Ingest service MVP
- InfluxDB persistence
- Vision pipeline planned
