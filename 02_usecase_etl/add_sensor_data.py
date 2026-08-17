#!/usr/bin/env python3
"""
add_sensor_data.py
==================
Workshop Utility: Insert new randomized IoT sensor telemetry readings
into the raw_sensor_readings table so Airflow DAGs have fresh data to process.

Usage:
    python3 add_sensor_data.py                     # Add 1 batch (3 readings per device)
    python3 add_sensor_data.py --batches 3         # Add 3 batches
    python3 add_sensor_data.py --anomaly           # Force an overheat reading (>75C)
    python3 add_sensor_data.py --reset             # Clear ALL data and re-seed fresh
"""

import argparse
import random
import psycopg2
from datetime import datetime, timezone

# --- Database Connection Settings ---
DB_CONFIG = {
    "host": "192.168.100.102",  # Workshop lab default; change to your DB host/IP if different.
    "port": 5433,
    "dbname": "iot_telemetry",
    "user": "iot_user",
    "password": "iot_password",
}

# --- Workshop IoT Device Fleet ---
DEVICES = [
    {"device_id": "IOT-NODE-ALPHA", "location": "Server Room A"},
    {"device_id": "IOT-NODE-BETA",  "location": "Warehouse North"},
    {"device_id": "IOT-NODE-GAMMA", "location": "HVAC Plant 01"},
    {"device_id": "IOT-NODE-DELTA", "location": "Data Center B"},
]


def connect():
    return psycopg2.connect(**DB_CONFIG)


def insert_readings(conn, readings):
    sql = """
        INSERT INTO raw_sensor_readings
        (device_id, location, temperature_celsius, humidity_pct, battery_pct, reading_timestamp, processed)
        VALUES (%s, %s, %s, %s, %s, %s, FALSE)
    """
    with conn.cursor() as cur:
        for r in readings:
            cur.execute(sql, (
                r["device_id"], r["location"],
                r["temp"], r["humidity"], r["battery"],
                r["ts"]
            ))
    conn.commit()


def generate_batch(force_anomaly=False):
    readings = []
    now = datetime.now(timezone.utc)
    for i, device in enumerate(DEVICES):
        if force_anomaly and i == 0:
            # Force a CRITICAL overheat on the first device
            temp = round(random.uniform(85.0, 95.0), 2)
        elif force_anomaly and i == 2:
            # Force a HIGH warning on the third device
            temp = round(random.uniform(75.5, 84.9), 2)
        else:
            # Normal operating range with occasional variance
            temp = round(random.uniform(18.0, 72.0), 2)

        readings.append({
            "device_id": device["device_id"],
            "location":  device["location"],
            "temp":      temp,
            "humidity":  round(random.uniform(25.0, 70.0), 2),
            "battery":   round(random.uniform(65.0, 100.0), 2),
            "ts":        now,
        })
    return readings


def reset_and_reseed(conn):
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE raw_sensor_readings RESTART IDENTITY CASCADE;")
        cur.execute("TRUNCATE TABLE daily_sensor_metrics RESTART IDENTITY CASCADE;")
        cur.execute("TRUNCATE TABLE sensor_alerts RESTART IDENTITY CASCADE;")
        cur.execute("TRUNCATE TABLE sensor_maintenance_queue RESTART IDENTITY CASCADE;")
    conn.commit()
    print("✅ All tables cleared and reset.")
    # Re-seed baseline readings
    seed_readings = [
        ("IOT-NODE-ALPHA", "Server Room A",   22.4, 45.2, 98.0),
        ("IOT-NODE-ALPHA", "Server Room A",   23.1, 44.8, 97.5),
        ("IOT-NODE-ALPHA", "Server Room A",   82.5, 41.0, 97.0),
        ("IOT-NODE-BETA",  "Warehouse North", 18.5, 62.0, 89.0),
        ("IOT-NODE-BETA",  "Warehouse North", 19.2, 60.5, 88.5),
        ("IOT-NODE-BETA",  "Warehouse North", 18.9, 61.2, 88.0),
        ("IOT-NODE-GAMMA", "HVAC Plant 01",   65.0, 30.0, 72.0),
        ("IOT-NODE-GAMMA", "HVAC Plant 01",   78.4, 28.5, 71.5),
        ("IOT-NODE-GAMMA", "HVAC Plant 01",   89.1, 25.0, 71.0),
    ]
    now = datetime.now(timezone.utc)
    sql = """
        INSERT INTO raw_sensor_readings
        (device_id, location, temperature_celsius, humidity_pct, battery_pct, reading_timestamp, processed)
        VALUES (%s, %s, %s, %s, %s, %s, FALSE)
    """
    with conn.cursor() as cur:
        for row in seed_readings:
            cur.execute(sql, (*row, now))
    conn.commit()
    print(f"✅ Re-seeded {len(seed_readings)} baseline readings.")


def print_summary(readings):
    print("\n📡 New Sensor Readings Inserted:")
    print(f"{'Device':<20} {'Location':<20} {'Temp':>8} {'Humidity':>10} {'Battery':>10} {'Alert':>8}")
    print("-" * 80)
    for r in readings:
        alert = "⚠️  HIGH" if r["temp"] >= 75.0 else ("🔴 CRIT" if r["temp"] >= 85.0 else "✅ OK")
        print(f"{r['device_id']:<20} {r['location']:<20} {r['temp']:>7.1f}°C {r['humidity']:>9.1f}% {r['battery']:>9.1f}% {alert:>8}")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Workshop: Add IoT sensor readings to database")
    parser.add_argument("--batches",  type=int, default=1, help="Number of batches to insert (default: 1)")
    parser.add_argument("--anomaly",  action="store_true", help="Force anomalous overheat readings")
    parser.add_argument("--reset",    action="store_true", help="Clear all tables and re-seed baseline data")
    args = parser.parse_args()

    conn = connect()
    print(f"🔌 Connected to {DB_CONFIG['host']}:{DB_CONFIG['port']} / {DB_CONFIG['dbname']}")

    if args.reset:
        reset_and_reseed(conn)
    else:
        all_readings = []
        for i in range(args.batches):
            batch = generate_batch(force_anomaly=args.anomaly)
            insert_readings(conn, batch)
            all_readings.extend(batch)
            print(f"✅ Batch {i+1}/{args.batches} inserted ({len(batch)} readings).")
        print_summary(all_readings)
        print(f"👉 Now trigger your Airflow DAGs to process {len(all_readings)} new unprocessed readings!")

    conn.close()
