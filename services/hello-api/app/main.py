import json
import os
import threading
import time
from collections import deque
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Deque, Dict, Optional

import paho.mqtt.client as mqtt
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

from dotenv import load_dotenv

load_dotenv() 


# ----------------------------
# Config (env vars)
# ----------------------------
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

BASE_TOPIC = os.getenv("BASE_TOPIC", "tennis/sensor/1/events")
PUB_TOPIC = os.getenv("PUB_TOPIC", BASE_TOPIC)
SUB_TOPIC = os.getenv("SUB_TOPIC", BASE_TOPIC)

EVENT_BUFFER_MAX = int(os.getenv("EVENT_BUFFER_MAX", "100"))

# (Optional later) InfluxDB config placeholders (we’ll use in Phase 1 persistence step)
INFLUX_ENABLED = os.getenv("INFLUX_ENABLED", "0") == "1"
INFLUX_HOST = os.getenv("INFLUX_HOST", "http://localhost:8181")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "")
INFLUX_DATABASE = os.getenv("INFLUX_DATABASE", "tennis")
INFLUX_TABLE = os.getenv("INFLUX_TABLE", "events")


# ----------------------------
# In-memory event buffer (debug window)
# ----------------------------
EVENTS: Deque[Dict[str, Any]] = deque(maxlen=EVENT_BUFFER_MAX)
EVENTS_LOCK = threading.Lock()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ----------------------------
# FastAPI app (lifespan replaces deprecated on_event)
# ----------------------------
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="hello-api")

mqtt_thread: Optional[threading.Thread] = None


def normalize_event(topic: str, payload_obj: Any) -> Dict[str, Any]:
    """
    Convert raw incoming data into a consistent "event envelope".
    This is important because later DB storage + dashboards LOVE consistency.
    """
    # If publisher already sends ts, we keep it. Otherwise we attach one.
    ts = None
    if isinstance(payload_obj, dict):
        ts = payload_obj.get("ts")

    return {
        "ts": ts or now_iso(),
        "topic": topic,
        "source": "mqtt",
        "payload": payload_obj,
    }


# MQTT callbacks
def on_connect(client, userdata, flags, rc, properties=None):
    print("[MQTT] connected rc=", rc)
    client.subscribe(SUB_TOPIC)
    print("[MQTT] subscribed to:", SUB_TOPIC)


def on_message(client, userdata, msg):
    raw = None
    try:
        raw = msg.payload.decode("utf-8", errors="replace")
    except Exception as e:
        print("[MQTT] payload decode error:", e)
        return

    # Step 1: decode JSON (because our payload is supposed to be JSON)
    try:
        payload_obj = json.loads(raw)
    except Exception:
        # If someone publishes non-JSON, we still store it as text for debugging
        payload_obj = {"_raw": raw, "_note": "non-json payload"}

    # Step 2: normalize into a standard envelope
    ev = normalize_event(msg.topic, payload_obj)

    # Step 3: store into memory buffer (last N)
    with EVENTS_LOCK:
        EVENTS.append(ev)

    print(f"[MQTT] RX {msg.topic} -> {raw}")

    # Step 4 (later): write to InfluxDB if enabled
    if INFLUX_ENABLED:
        try:
            write_event_to_influx(ev)
        except Exception as e:
            print("[INFLUX] write error:", e)


def mqtt_worker():
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    while True:
        try:
            print(f"[MQTT] connecting to {MQTT_HOST}:{MQTT_PORT} ...")
            mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
            mqtt_client.loop_forever()  # blocks until disconnect/error
        except Exception as e:
            print("[MQTT] error, retrying in 3s:", e)
            time.sleep(3)


# ----------------------------
# InfluxDB 3 write (Phase 1 persistence)
# ----------------------------

def iso_to_epoch_seconds(ts: str) -> int:
    # Handles ISO like "2026-02-10T16:59:10.239950Z" or with +00:00
    ts = ts.replace("Z", "+00:00")
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp())


def write_event_to_influx(ev: Dict[str, Any]) -> None:
    """
    Minimal InfluxDB 3 write path.
    We’ll keep it simple: write one event as line protocol into a table.

    NOTE: InfluxDB 3 uses line protocol and tables. :contentReference[oaicite:2]{index=2}
    We’ll implement the full version once Influx is running + token is set.
    """
    # Lazy import so Phase 0.5 still runs without the dependency installed
    from influxdb_client_3 import InfluxDBClient3  # influxdb3-python

    if not INFLUX_TOKEN:
        raise RuntimeError("INFLUX_ENABLED=1 but INFLUX_TOKEN is empty")

    client = InfluxDBClient3(
        host=INFLUX_HOST,
        token=INFLUX_TOKEN,
        database=INFLUX_DATABASE,
    )

    # Build line protocol:
    # table,tagKey=tagVal fieldKey="value" timestamp
    # We’ll store event_type/topic as tags for easy filtering.
    topic = ev.get("topic", "unknown")
    ts_epoch = iso_to_epoch_seconds(ev.get("ts") or now_iso())

    # store payload as JSON string field (simple MVP)
    payload_str = json.dumps(ev.get("payload", {}), ensure_ascii=False)

    # line protocol: measurement,tag=value field="..." timestamp
    # tags: keep simple for now (topic as a tag)
    escaped_payload = payload_str.replace('"', '\\"')
    line = f'{INFLUX_TABLE},topic={topic} payload="{escaped_payload}" {ts_epoch}'

    client.write(record=line, write_precision="s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    global mqtt_thread
    mqtt_thread = threading.Thread(target=mqtt_worker, daemon=True)
    mqtt_thread.start()
    print("[APP] startup complete")

    yield

    # SHUTDOWN (best-effort)
    try:
        mqtt_client.disconnect()
    except Exception:
        pass
    print("[APP] shutdown complete")


app = FastAPI(title="hello-api", version="0.2.0", lifespan=lifespan)


# ----------------------------
# REST endpoints
# ----------------------------
@app.get("/health")
def health():
    return {"status": "ok", "service": "hello-api"}


@app.get("/events")
def get_events(limit: int = Query(50, ge=1, le=EVENT_BUFFER_MAX)):
    """
    Returns last N events from memory.
    This is your “debug window” to prove ingestion works.
    """
    with EVENTS_LOCK:
        items = list(EVENTS)[-limit:]
    return {"count": len(items), "events": items}


class PublishIn(BaseModel):
    topic: str = Field(default=PUB_TOPIC)
    payload: Dict[str, Any]


@app.post("/publish")
def publish(data: PublishIn):
    mqtt_client.publish(data.topic, json.dumps(data.payload), qos=0)
    return {"sent": True, "topic": data.topic, "payload": data.payload}


print("INFLUX TOKEN LOADED:", bool(INFLUX_TOKEN))
