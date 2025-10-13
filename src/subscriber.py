import os, json
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

load_dotenv()
HOST = os.getenv("BROKER_HOST","localhost")
PORT = int(os.getenv("BROKER_PORT","1883"))
USER = os.getenv("BROKER_USERNAME") or None
PWD  = os.getenv("BROKER_PASSWORD") or None
USE_TLS = os.getenv("USE_TLS","false").lower()=="true"

def on_connect(c,u,f,rc,props=None):
    print(f"[SUB] on_connect rc={rc} (0=OK)")
    c.subscribe("veh/#")

def on_message(c,u,msg):
    try:
        data = json.loads(msg.payload.decode())
    except Exception:
        data = msg.payload.decode(errors="ignore")
    print(f"{msg.topic:<12} {data}")

client = mqtt.Client(client_id="car-sub")   # <— DIFFERENT FROM SIM
client.enable_logger()
if USER and PWD: client.username_pw_set(USER, PWD)
if USE_TLS: client.tls_set()

client.on_connect = on_connect
client.on_message = on_message

print(f"[SUB] Connecting to {HOST}:{PORT} TLS={'on' if USE_TLS else 'off'}")
client.connect(HOST, PORT, keepalive=30)
client.loop_forever()
