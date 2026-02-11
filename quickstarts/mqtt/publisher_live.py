import json, time
import paho.mqtt.client as mqtt
from datetime import datetime

BROKER = "localhost"
PORT   = 1883
TOPIC  = "tennis/sensor/1/events"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="publisher-1")

def on_connect(client, userdata, flags, rc, properties=None):
    print("Publisher connected rc=", rc)

print(f"[PUB] connecting to {BROKER}:{PORT}")
client.on_connect = on_connect
client.connect(BROKER, PORT, 60)
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
