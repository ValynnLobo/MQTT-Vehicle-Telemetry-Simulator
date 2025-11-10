import json, os, sys, time, subprocess, signal
from pathlib import Path
from jsonschema import validate, ValidationError

# Make src importable when running `pytest` from project root
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
import topics
from schema import payload_schema

BROKER_HOST = os.getenv("BROKER_HOST", "localhost")
BROKER_PORT = int(os.getenv("BROKER_PORT", "1883"))

import paho.mqtt.client as mqtt

def launch_sim():
    # start the simulator as a child process
    return subprocess.Popen([sys.executable, "src/simulator.py"],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)

def collect_messages(duration=2.0):
    msgs = {topics.RPM: [], topics.THROTTLE: [], topics.SPEED: []}

    def on_connect(c, u, f, rc, props=None):
        assert rc == 0, f"MQTT connect failed rc={rc}"
        c.subscribe([(topics.RPM, 0), (topics.THROTTLE, 0), (topics.SPEED, 0)])

    def on_message(c, u, m):
        try:
            data = json.loads(m.payload.decode())
            msgs[m.topic].append((m.timestamp if hasattr(m, "timestamp") else time.time(), data))
        except Exception:
            pass

    client = mqtt.Client(client_id="test-sub")
    if os.getenv("BROKER_USERNAME") and os.getenv("BROKER_PASSWORD"):
        client.username_pw_set(os.getenv("BROKER_USERNAME"), os.getenv("BROKER_PASSWORD"))
    if os.getenv("USE_TLS", "false").lower() == "true":
        client.tls_set()

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_HOST, BROKER_PORT, 30)
    client.loop_start()
    t0 = time.time()
    while time.time() - t0 < duration:
        time.sleep(0.05)
    client.loop_stop()
    client.disconnect()
    return msgs

def _rate_ok(timestamps, expect_hz=10.0, tolerance=0.35):
    if len(timestamps) < 2:
        return False
    dts = [b - a for a, b in zip(timestamps[:-1], timestamps[1:])]
    if not dts:
        return False
    median_dt = sorted(dts)[len(dts)//2]
    return abs((1.0/median_dt) - expect_hz) <= (expect_hz * tolerance)

def test_stream_rate_and_schema():
    sim = launch_sim()
    try:
        msgs = collect_messages(duration=2.0)  # ~20 messages per topic expected

        # 1) each topic received enough messages
        for t in (topics.RPM, topics.THROTTLE, topics.SPEED):
            assert len(msgs[t]) >= 15, f"too few messages on {t}: {len(msgs[t])}"

        # 2) schema + value ranges
        for t, arr in msgs.items():
            ts_only = []
            for ts, payload in arr:
                # schema valid
                validate(instance=payload, schema=payload_schema)
                # ranges
                v = payload["value"]
                if t == topics.RPM:
                    assert 0 <= v <= 7000
                elif t == topics.THROTTLE:
                    assert 0 <= v <= 100
                elif t == topics.SPEED:
                    assert 0 <= v <= 300
                ts_only.append(ts)
            # 3) approximate 10 Hz rate (within tolerance)
            assert _rate_ok(ts_only, expect_hz=10.0), f"rate check failed for {t}"
    finally:
        # terminate simulator
        try:
            sim.send_signal(signal.CTRL_BREAK_EVENT if os.name == "nt" else signal.SIGTERM)
            sim.wait(timeout=2)
        except Exception:
            sim.kill()
