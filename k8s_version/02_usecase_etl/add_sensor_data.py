import argparse
import random
from datetime import datetime

import psycopg2

DB = {
    "host": "localhost",
    "port": 5433,
    "dbname": "iot_telemetry",
    "user": "iot_user",
    "password": "iot_password",
}

DEVICES = [
    ("IOT-NODE-ALPHA", "Server Room A"),
    ("IOT-NODE-BETA", "Warehouse North"),
    ("IOT-NODE-GAMMA", "HVAC Plant 01"),
    ("IOT-NODE-DELTA", "Data Center B"),
]


def insert_batch(conn, anomaly=False):
    with conn.cursor() as cur:
        for device, loc in DEVICES:
            t = random.uniform(18, 30)
            if anomaly and random.random() < 0.4:
                t = random.uniform(76, 92)
            h = random.uniform(30, 70)
            b = random.uniform(50, 100)
            cur.execute(
                """
                INSERT INTO raw_sensor_readings
                (device_id, location, temperature_celsius, humidity_pct, battery_pct, reading_timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (device, loc, round(t, 2), round(h, 2), round(b, 2), datetime.utcnow()),
            )
    conn.commit()


def reset_all(conn):
    with conn.cursor() as cur:
        cur.execute(
            "TRUNCATE sensor_alerts, daily_sensor_metrics, raw_sensor_readings RESTART IDENTITY CASCADE;"
        )
    conn.commit()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--batches", type=int, default=1)
    p.add_argument("--anomaly", action="store_true")
    p.add_argument("--reset", action="store_true")
    args = p.parse_args()

    conn = psycopg2.connect(**DB)
    try:
        if args.reset:
            reset_all(conn)
            print("reset complete")
        else:
            for _ in range(args.batches):
                insert_batch(conn, anomaly=args.anomaly)
            print(f"inserted {args.batches} batch(es)")
    finally:
        conn.close()
