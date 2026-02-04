import paho.mqtt.client as mqtt
BROKER="localhost"; PORT=2883; TOPIC="tennis/hello"

c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="sub-hello")
def on_connect(client, userdata, flags, rc, properties=None):
    print("connected", rc); client.subscribe(TOPIC)
def on_message(client, userdata, msg):
    print(msg.topic, msg.payload.decode())

c.on_connect=on_connect; c.on_message=on_message
c.connect(BROKER, PORT, 60)
c.loop_forever()
