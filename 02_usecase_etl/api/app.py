from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
import psycopg2.extras

app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    "host": "iot_telemetry_db",  # Docker network service name
    "port": 5432,
    "dbname": "iot_telemetry",
    "user": "iot_user",
    "password": "iot_password",
}


def get_conn():
    return psycopg2.connect(**DB_CONFIG)


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/raw-readings")
def raw_readings():
    conn = get_conn()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("""
            SELECT reading_id, device_id, location,
                   ROUND(temperature_celsius::numeric, 1) AS temperature_celsius,
                   ROUND(humidity_pct::numeric, 1) AS humidity_pct,
                   ROUND(battery_pct::numeric, 1) AS battery_pct,
                   processed,
                   TO_CHAR(reading_timestamp AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS') AS reading_timestamp
            FROM raw_sensor_readings
            ORDER BY reading_timestamp DESC
            LIMIT 50;
        """)
        rows = cur.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/metrics")
def metrics():
    conn = get_conn()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("""
            SELECT device_id, location,
                   ROUND(avg_temperature::numeric, 1) AS avg_temperature,
                   ROUND(max_temperature::numeric, 1) AS max_temperature,
                   ROUND(min_temperature::numeric, 1) AS min_temperature,
                   total_readings,
                   TO_CHAR(calculated_at AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS') AS computed_at
            FROM daily_sensor_metrics
            ORDER BY avg_temperature DESC;
        """)
        rows = cur.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/alerts")
def alerts():
    conn = get_conn()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("""
            SELECT alert_id, device_id, alert_type,
                   ROUND(metric_value::numeric, 1) AS metric_value,
                   ROUND(threshold_value::numeric, 1) AS threshold_value,
                   severity,
                   TO_CHAR(alert_timestamp AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS') AS triggered_at
            FROM sensor_alerts
            ORDER BY alert_timestamp DESC;
        """)
        rows = cur.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/maintenance")
def maintenance():
    conn = get_conn()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("""
            SELECT ticket_id, device_id, location,
                   ROUND(current_temp::numeric, 1) AS current_temp,
                   risk_level, priority_score, recommended_action, status,
                   TO_CHAR(created_at AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI:SS') AS created_at
            FROM sensor_maintenance_queue
            ORDER BY priority_score DESC;
        """)
        rows = cur.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/stats")
def stats():
    """Summary stats card for dashboard header"""
    conn = get_conn()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT COUNT(*) AS total FROM raw_sensor_readings;")
        total_raw = cur.fetchone()["total"]
        cur.execute("SELECT COUNT(*) AS total FROM raw_sensor_readings WHERE processed = FALSE;")
        unprocessed = cur.fetchone()["total"]
        cur.execute("SELECT COUNT(*) AS total FROM sensor_alerts;")
        total_alerts = cur.fetchone()["total"]
        cur.execute("SELECT COUNT(*) AS total FROM sensor_maintenance_queue WHERE status = 'OPEN';")
        open_tickets = cur.fetchone()["total"]
        cur.execute("SELECT COUNT(DISTINCT device_id) AS total FROM raw_sensor_readings;")
        devices = cur.fetchone()["total"]
    conn.close()
    return jsonify({
        "total_raw_readings": total_raw,
        "unprocessed_readings": unprocessed,
        "total_alerts": total_alerts,
        "open_maintenance_tickets": open_tickets,
        "active_devices": devices,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
