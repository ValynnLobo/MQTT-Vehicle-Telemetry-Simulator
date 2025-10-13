import os, json, time, socket
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

load_dotenv()
HOST = os.getenv("BROKER_HOST","localhost")
PORT = int(os.getenv("BROKER_PORT","1883"))
USER = os.getenv("BROKER_USERNAME") or None
PWD  = os.getenv("BROKER_PASSWORD") or None
USE_TLS = os.getenv("USE_TLS","false").lower()=="true"

print("ENV →", {"HOST":HOST, "PORT":PORT, "TLS":USE_TLS, "USER?":bool(USER)})

# quick TCP reachability
s = socket.socket()
s.settimeout(3)
try:
    s.connect((HOST, PORT))
    print("TCP → reachable ✅")
    s.close()
except Exception as e:
    print("TCP → cannot connect ❌:", repr(e))

def on_connect(c,u,f,rc,props=None):
    print("MQTT on_connect rc=", rc, "(0=OK, 5=Auth fail)")
    if rc==0:
        c.subscribe("veh/diag")
        c.publish("veh/diag", json.dumps({"ts":time.time(),"ping":"pong"}), qos=0)

def on_message(c,u,msg):
    print("MQTT recv →", msg.topic, msg.payload.decode(errors="ignore"))
    c.disconnect()

client = mqtt.Client(client_id="diag-client")
client.enable_logger()           # verbose logs
if USER and PWD: client.username_pw_set(USER,PWD)
if USE_TLS: client.tls_set()

client.on_connect = on_connect
client.on_message = on_message

print("Connecting…")
client.connect(HOST, PORT, keepalive=20)
client.loop_forever()
