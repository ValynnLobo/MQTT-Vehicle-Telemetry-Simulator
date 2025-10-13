import json, os, random, time
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
import topics

load_dotenv()
HOST = os.getenv("BROKER_HOST", "localhost")
PORT = int(os.getenv("BROKER_PORT", "1883"))
USER = os.getenv("BROKER_USERNAME") or None
PWD  = os.getenv("BROKER_PASSWORD") or None
USE_TLS = os.getenv("USE_TLS", "false").lower() == "true"

client = mqtt.Client(client_id="car-sim")
if USER and PWD:
    client.username_pw_set(USER, PWD)
if USE_TLS:
    client.tls_set()  # system CAs

client.connect(HOST, PORT, keepalive=30)
client.loop_start()

def payload(ts, value):
    return json.dumps({"ts": ts, "value": value})

try:
    while True:
        ts = time.time()
        rpm = random.randint(800, 3200)
        thr = random.randint(0, 100)
        spd = random.randint(0, 120)
        client.publish(topics.RPM,      payload(ts, rpm), qos=0, retain=False)
        client.publish(topics.THROTTLE, payload(ts, thr), qos=0, retain=False)
        client.publish(topics.SPEED,    payload(ts, spd), qos=0, retain=False)
        time.sleep(0.1)  # 10 Hz
except KeyboardInterrupt:
    pass
finally:
    client.loop_stop()
    client.disconnect()
