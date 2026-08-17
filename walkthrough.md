# Workshop Walkthrough: Apache Airflow Local Lab

This document is a reusable execution record for running the workshop locally.
Replace placeholders as needed for your environment.

---

## 🖥️ Local Environment Snapshot

| Property | Value |
| :--- | :--- |
| **Host Type** | Local VM/workstation/server |
| **OS** | `<your-os>` |
| **Host Access** | Local shell or `ssh <user>@<HOST_IP>` |
| **Airflow Web UI** | `http://localhost:8080` (`admin` / `admin`) |
| **IoT Database** | `localhost:5433` (`iot_user` / `iot_password`, DB: `iot_telemetry`) |
| **ETL Dashboard** | `http://localhost:3001` |

---

## 🛠️ Deployment Steps Completed

### 1) Base setup
- Installed Docker Engine + Docker Compose v2.
- Prepared project folders and required permissions.

### 2) Airflow core stack
- Initialized metadata DB via `airflow-init`.
- Started `airflow_webserver`, `airflow_scheduler`, `airflow_triggerer`, `airflow_postgres`.

### 3) ETL + visualization stack
- Started `iot_telemetry_db` with `init.sql` seed data.
- Started `iot_api` and `airflow_dashboard`.
- Registered `iot_db_conn` Airflow connection.

### 4) Manual DAG exercise setup
- Applied `init_maintenance_schema.sql`.
- Staged `manual_sensor_cleaning_dag.py` into Airflow DAG folder.

---

## 🐳 Example Container Status

```text
NAME                IMAGE                              STATUS          PORTS
airflow_dashboard   02_usecase_etl-airflow-dashboard   Up (healthy)    0.0.0.0:3001->80/tcp
iot_telemetry_db    postgres:15-alpine                 Up (healthy)    0.0.0.0:5433->5432/tcp
airflow_webserver   apache/airflow:2.10.0              Up (healthy)    0.0.0.0:8080->8080/tcp
airflow_scheduler   apache/airflow:2.10.0              Up (healthy)    8080/tcp
airflow_triggerer   apache/airflow:2.10.0              Up (healthy)    8080/tcp
airflow_postgres    postgres:15-alpine                 Up (healthy)    5432/tcp
```

---

## ✅ Example Verification Results

### DAG: `iot_telemetry_etl`
```text
dag_id            | run_id                               | state
==================+======================================+=========
iot_telemetry_etl | manual__<timestamp>                  | success
```

### `daily_sensor_metrics` sample
```text
 device_id      | avg_temperature | max_temperature | min_temperature | total_readings
----------------+-----------------+-----------------+-----------------+----------------
 IOT-NODE-ALPHA |           42.67 |           82.50 |           22.40 |              3
 IOT-NODE-BETA  |           18.87 |           19.20 |           18.50 |              3
 IOT-NODE-GAMMA |           77.50 |           89.10 |           65.00 |              3
```

### `sensor_alerts` sample (>75°C)
```text
 device_id      | alert_type       | metric_value | threshold_value | severity
----------------+------------------+--------------+-----------------+----------
 IOT-NODE-ALPHA | HIGH_TEMPERATURE |        82.50 |           75.00 | WARNING
 IOT-NODE-GAMMA | HIGH_TEMPERATURE |        89.10 |           75.00 | WARNING
```

---

## 📚 Module Inventory

| Module | Folder | Purpose |
| :--- | :--- | :--- |
| **01** | [`01_install/`](./01_install/README.md) | Docker Compose Airflow core setup |
| **02** | [`02_usecase_etl/`](./02_usecase_etl/README.md) | IoT TaskFlow ETL + API + dashboard |
| **03** | [`03_operational_painpoints/`](./03_operational_painpoints/README.md) | Operational troubleshooting guide |
| **04** | [`04_manual_dag_exercise/`](./04_manual_dag_exercise/README.md) | Manual DAG creation exercise |
| **05** | [`05_git_based_dag_retrieval/`](./05_git_based_dag_retrieval/README.md) | Git-based DAG retrieval workflow demo |
