import json, time
import paho.mqtt.client as mqtt
from datetime import datetime

import os
BROKER = os.getenv("MQTT_HOST", "emqx")
PORT = int(os.getenv("MQTT_PORT", "1883"))
TOPIC  = "tennis/sensor/1/events"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="publisher-1")

def on_connect(client, userdata, flags, rc, properties=None):
    print("Publisher connected rc=", rc)

while True:
    try:
        print(f"[PUB] connecting to {BROKER}:{PORT}")
        client.connect(BROKER, PORT, 60)
        break
    except Exception as e:
        print("[PUB] broker not ready, retry in 2s:", e)
        time.sleep(2)
        
client.loop_start()

try:
    while True:
        payload = {"sensor_id": 1, "event": "serve_impact", "ts": datetime.utcnow().isoformat()}
        client.publish(TOPIC, json.dumps(payload), qos=0)
        print("[PUB] sent:", payload)
        time.sleep(2)
except KeyboardInterrupt:
    print("Stopping publisher...")
finally:
    client.loop_stop()
    client.disconnect()
