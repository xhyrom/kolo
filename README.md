**kolo** is a telemetry and dashboard system designed for real-time vehicle velocity monitoring using a wireless BLE sensor written in **python**.

## Why?

**kolo** is a custom-built monitoring solution split into two simple parts. 
It is designed to collect data from sensors via bluetooth and display it in a clean, real-time dashboard without any unnecessary bloat. Mainly used for tracking vehicle data on the fly.

## Components

**whub** is the wireless hub. It runs in the background, connecting to sensors via **BLE** to process raw telemetry data and broadcast it over the network.

**wall** is the visual frontend. It receives the broadcasted data and plots live graphs of speed and acceleration using **matplotlib**. It also manages recording sessions, letting you tag and export data effortlessly.

## Usage

Both components use standard `pyproject.toml` configurations.

```bash
cd wall
python -m wall
```

## Storage

Sessions are automatically saved into `wall/data/`. You can append a custom suffix via the dashboard UI to easily identify your runs alongside the timestamps.
