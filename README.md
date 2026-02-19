🎾 Smart Tennis Field — IoT Event Pipeline (Docker Edition)
📌 Overview

This project implements a Smart Tennis Field architecture using:

🟢 EMQX (MQTT Broker)

🔵 InfluxDB 3 Core (Time-series database)

🟣 FastAPI Ingest Service

🟡 Sensor Simulator (Fake publisher)

All services run using Docker Compose.

🏗 Architecture
Sensor Simulator  →  EMQX (MQTT Broker)
                        ↓
                 Ingest Service (Subscriber)
                        ↓
                  InfluxDB 3 Core

Flow:

Sensor simulator publishes fake tennis events

EMQX handles message routing

Ingest service subscribes to:

tennis/sensor/+/events


Events are:

Normalized

Validated

Stored in InfluxDB

🚀 How to Run (Docker Compose Only)

⚠️ Old manual Python execution is removed.
Everything runs through Docker.

1️⃣ Start All Services

From project root:

docker compose up --build


To run in background:

docker compose up -d --build

2️⃣ Check Running Services
docker compose ps

3️⃣ Stop Services
docker compose down


⚠️ DO NOT use:

docker compose down -v


This deletes InfluxDB data and your token.

🔐 Creating InfluxDB Admin Token

InfluxDB 3 Core does NOT auto-generate a persistent token for you.

After starting containers:

docker exec -it influxdb3 influxdb3 create token --admin


It will output something like:

Token: eyJhbGciOi...


Copy this token.

Add Token to .env

Create or update .env file in project root:

INFLUX_TOKEN=YOUR_TOKEN_HERE
INFLUX_ENABLED=1


Example:

INFLUX_TOKEN=eyJhbGciOi...
INFLUX_ENABLED=1


Then restart ingest service:

docker compose restart ingest-service

🌐 Service Endpoints
EMQX Dashboard
http://localhost:18083

InfluxDB 3
http://localhost:8181

Ingest Service API
http://localhost:8000

📡 Available API Endpoints
Health Check
GET /health

Get Recent Events
GET /events?limit=10

Publish Test Event
POST /publish

📁 Project Structure
services/
  ingest_service/
    app/
      main.py
      mqtt.py
      influx.py
      config.py

quickstarts/
  mqtt/
    Dockerfile.sensor

docker-compose.yml
.env

🧠 Development Philosophy

Sensors are currently simulated (fake data)

Architecture is production-ready

Real camera + YOLO pipeline can replace sensor-sim later

Backend remains unchanged

🔄 If You Lose Token

If you accidentally delete volume:

docker compose down -v


You must:

Restart containers

Recreate admin token

Update .env

Restart ingest-service

📌 Current Phase

✅ MQTT Working
✅ Ingest Service MVP
✅ InfluxDB Persistence
🚧 Vision Pipeline (Planned)