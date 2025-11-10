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
