# MQTT Car Simulator

A lightweight Python-based car telemetry simulator that publishes and subscribes to MQTT topics, enabling control of throttle, speed, and simulated fault states. The project supports record–replay functionality and can be used to test MQTT-based systems, dashboards, or IoT applications.

---

## Overview

This simulator mimics basic vehicle telemetry over MQTT, sending randomized or replayed data such as:
- Engine RPM  
- Throttle position  
- Vehicle speed  
- System status (online/offline)  
- Command controls (set speed, throttle, fault)

It can connect to any MQTT broker and is easily configurable through environment variables.

---

## Features

- **MQTT-based Telemetry Simulation**  
  Publishes RPM, throttle, and speed data periodically.

- **Command Topic Support**  
  Responds to control topics such as:  
  - `veh/throttle_cmd`  
  - `veh/set_speed`  
  - `veh/fault`

- **Record & Replay Mode**  
  Replays CSV telemetry data for repeatable testing.

- **Environment Configuration**  
  Broker details and credentials loaded from `.env`.

- **Docker-ready**  
  The project can be containerized and run with minimal setup.

---

## Installation

### Prerequisites
- Python 3.9 or higher  
- [Eclipse Mosquitto](https://mosquitto.org/download/) or any MQTT broker  
- `virtualenv` for isolated environment setup

### Setup

```bash
# Clone the repository
git clone https://github.com/<your-username>/mqtt-car-sim.git
cd mqtt-car-sim

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate     # On Windows
source .venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

---

## Configuration
``` python
BROKER_HOST = "localhost"
BROKER_PORT = 1883
TLS_ENABLED = False

CAR_COUNT = 5
PUBLISH_INTERVAL = 2  # seconds
TOPIC = "cars/telemetry"

# to connect to a different MQTT broker:
BROKER_HOST = "test.mosquitto.org"
BROKER_PORT = 1883
TLS_ENABLED = True
```

---

## Running the Simulator
From the src directory run:

```bash
python simulator.py
```

Expected output:
```csharp
[SIM] Connecting to localhost:1883 TLS=off QoS=1
[SIM] on_connect rc=0 (0=OK)
[SIM] Car-01 publishing to cars/telemetry: {"speed": 74, "fuel": 68, "lat": -37.81, "lon": 144.96}
```

You can verify messages with a local MQTT client:
```bash
mosquitto_sub -h localhost -t "cars/telemetry"
```

---

## Record & Replay
You can replay recorded telemetry data from a CSV file by setting:

```ini
REPLAY_FILE=data/session1.csv
```
Each row should include columns like: timestamp, rpm, throttle, speed

---

## License
© 2025 Valynn Lobo. All rights reserved. This is a personal learning project.
