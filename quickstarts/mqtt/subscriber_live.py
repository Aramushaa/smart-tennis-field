import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT   = 1883
TOPIC  = "tennis/sensor/1/events"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="subscriber-1")

def on_connect(client, userdata, flags, rc, properties=None):
    print("Subscriber connected rc=", rc)
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    print(f"[SUB] {msg.topic} -> {msg.payload.decode()}")

print(f"[SUB] connecting to {BROKER}:{PORT}")
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.loop_forever()
