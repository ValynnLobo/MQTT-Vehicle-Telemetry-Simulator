import json, os, random, time, signal, sys, csv
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
import topics

load_dotenv()
HOST = os.getenv("BROKER_HOST", "localhost")
PORT = int(os.getenv("BROKER_PORT", "1883"))
USER = os.getenv("BROKER_USERNAME") or None
PWD  = os.getenv("BROKER_PASSWORD") or None
USE_TLS = os.getenv("USE_TLS", "false").lower() == "true"
CLIENT_ID = os.getenv("SIM_CLIENT_ID", "car-sim")
QOS = int(os.getenv("MQTT_QOS", "1"))

def encode(ts, value): 
    return json.dumps({"ts": ts, "value": value})

def on_connect(c, u, f, rc, props=None):
    print(f"[SIM] on_connect rc={rc} (0=OK)")

client = mqtt.Client(client_id=CLIENT_ID)
client.enable_logger()
if USER and PWD: client.username_pw_set(USER, PWD)
if USE_TLS: client.tls_set()
client.on_connect = on_connect

# Last Will
client.will_set(topics.STATUS, payload="offline", qos=QOS, retain=True)

print(f"[SIM] Connecting to {HOST}:{PORT} TLS={'on' if USE_TLS else 'off'} QoS={QOS}")
client.connect(HOST, PORT, keepalive=30)
client.loop_start()

# Birth
client.publish(topics.STATUS, payload="online", qos=QOS, retain=True)

# --- Simulator State ---
sim_state = {
    "throttle": 0.0,
    "speed": 0.0,
    "target_speed": 0.0,
    "fault": False
}

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()

    if topic == topics.CMD:
        throttle_value = float(payload)
        sim_state["throttle"] = throttle_value
        print(f"[SIM] Throttle set to {throttle_value}")

    elif topic == topics.CMD_SET_SPEED:
        sim_state["target_speed"] = float(payload)
        print(f"[SIM] Target speed set to {payload}")

    elif topic == topics.CMD_FAULT:
        if payload.lower() in ["on", "true", "1"]:
            sim_state["fault"] = True
            print("[SIM] FAULT ON")
        else:
            sim_state["fault"] = False
            print("[SIM] FAULT OFF")

client.on_message = on_message
client.subscribe(topics.CMD)
client.subscribe(topics.CMD_SET_SPEED)
client.subscribe(topics.CMD_FAULT)

# --- Replay setup ---
REPLAY_FILE = os.getenv("REPLAY_FILE")
replay_data = None
if REPLAY_FILE and os.path.exists(REPLAY_FILE):
    with open(REPLAY_FILE) as f:
        reader = csv.DictReader(f)
        replay_data = list(reader)
    print(f"[SIM] Loaded {len(replay_data)} rows from {REPLAY_FILE}")

_running = True
def _stop(*_):
    global _running
    _running = False
signal.signal(signal.SIGINT, _stop)
signal.signal(signal.SIGTERM, _stop)

try:
    if replay_data:
        for row in replay_data:
            ts = time.time()
            client.publish(topics.RPM, encode(ts, row.get("rpm", 0)), qos=QOS)
            client.publish(topics.THROTTLE, encode(ts, row.get("throttle", 0)), qos=QOS)
            client.publish(topics.SPEED, encode(ts, row.get("speed", 0)), qos=QOS)
            time.sleep(0.1)
    else:
        while _running:
            ts = time.time()
            client.publish(topics.RPM,      encode(ts, random.randint(800, 3200)), qos=QOS)
            client.publish(topics.THROTTLE, encode(ts, random.randint(0, 100)),    qos=QOS)
            client.publish(topics.SPEED,    encode(ts, random.randint(0, 120)),    qos=QOS)
            time.sleep(0.1)
finally:
    client.publish(topics.STATUS, payload="offline", qos=QOS, retain=True)
    client.loop_stop()
    client.disconnect()
    print("[SIM] stopped cleanly")