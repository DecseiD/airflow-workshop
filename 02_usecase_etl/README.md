# Module 02: End-to-End IoT Telemetry ETL + Before/After Dashboard

In Module 02, you deploy a dedicated PostgreSQL container (`iot_telemetry_db`), a live Flask API (`iot_api`), and a dashboard (`airflow_dashboard`) for visualizing ETL outcomes.

The dashboard refreshes every 15 seconds so inserted data and DAG outputs are visible in near real time.

---

## 1. Build and launch services

```bash
cd airflow/02_usecase_etl
docker compose -f docker-compose-db.yaml up -d --build
```

## 2. Verify runtime

```bash
docker compose -f docker-compose-db.yaml ps
curl http://localhost:5000/api/stats
```

Expected running services:
- `iot_telemetry_db` on `:5433`
- `iot_api` on `:5000`
- `airflow_dashboard` on `:3001`

---

## 3. Open dashboard

- Local: **[http://localhost:3001](http://localhost:3001)**
- Remote host browser: **[http://<HOST_IP>:3001](http://<HOST_IP>:3001)**

Panels shown:
1. Stats pills
2. Raw Sensor Log (before ETL)
3. Aggregated Device Metrics (after ETL)
4. Temperature Chart
5. Alerts Feed
6. Maintenance Queue (Module 04)

---

## 4. Generate live data (`add_sensor_data.py`)

```bash
cd airflow/02_usecase_etl

# normal batch
python3 add_sensor_data.py

# multiple batches
python3 add_sensor_data.py --batches 3

# force anomalies for demo
python3 add_sensor_data.py --anomaly

# reset all ETL tables
python3 add_sensor_data.py --reset
```

### Demo flow
1. Run `python3 add_sensor_data.py --anomaly`
2. Trigger `iot_telemetry_etl` in Airflow UI
3. Confirm metrics/alerts update in dashboard
4. Trigger `manual_sensor_maintenance_classifier` (Module 04)
5. Verify maintenance queue panel populates

---

## 5. Register `iot_db_conn` in Airflow

Run from `airflow/01_install` folder:

```bash
docker compose exec airflow-webserver airflow connections add 'iot_db_conn' \
    --conn-type 'postgres' \
    --conn-host 'iot_telemetry_db' \
    --conn-port '5432' \
    --conn-login 'iot_user' \
    --conn-password 'iot_password' \
    --conn-schema 'iot_telemetry'
```

---

## 6. Validate transformations with SQL

```bash
# daily metrics
docker exec -it iot_telemetry_db psql -U iot_user -d iot_telemetry -c "SELECT device_id, metric_date, avg_temperature, max_temperature FROM daily_sensor_metrics;"

# threshold alerts
docker exec -it iot_telemetry_db psql -U iot_user -d iot_telemetry -c "SELECT alert_id, device_id, metric_value, severity FROM sensor_alerts;"
```
