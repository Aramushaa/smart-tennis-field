import json
import os
import threading
import time

import paho.mqtt.client as mqtt
from fastapi import FastAPI
from pydantic import BaseModel

# mapped MQTT port (2883)
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "2883"))

SUB_TOPIC = os.getenv("SUB_TOPIC", "tennis/sensor/1/events")
PUB_TOPIC = os.getenv("PUB_TOPIC", "tennis/hello")

app = FastAPI(title="hello-api", version="0.1.0")

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="hello-api")

def on_connect(client, userdata, flags, rc, properties=None):
    print("[MQTT] connected rc=", rc)
    client.subscribe(SUB_TOPIC)
    print("[MQTT] subscribed to:", SUB_TOPIC)

def on_message(client, userdata, msg):
    try:
        print(f"[MQTT] RX {msg.topic} -> {msg.payload.decode()}")
    except Exception as e:
        print("[MQTT] decode error:", e)

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

@app.on_event("startup")
def startup():
    # run MQTT client in background thread so FastAPI can serve HTTP
    t = threading.Thread(target=mqtt_worker, daemon=True)
    t.start()

@app.get("/health")
def health():
    return {"status": "ok", "service": "hello-api"}

class PublishIn(BaseModel):
    topic: str = PUB_TOPIC
    payload: dict

@app.post("/publish")
def publish(data: PublishIn):
    mqtt_client.publish(data.topic, json.dumps(data.payload), qos=0)
    return {"sent": True, "topic": data.topic, "payload": data.payload}
