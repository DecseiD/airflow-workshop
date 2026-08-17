# Module 04: Manual DAG Creation & Live Enablement Exercise

Welcome to Module 04! This module provides a hands-on, step-by-step exercise for **creating, deploying, enabling, and triggering a new Airflow DAG live** during your workshop presentation.

This exercise utilizes your existing PostgreSQL IoT database (`iot_telemetry_db`) and existing telemetry data to demonstrate a stark, verifiable **Before vs. After state transformation**.

---

## 🎯 Exercise Scenario: Automated Hardware Maintenance Queue

### Problem Statement
Your operations team has raw sensor telemetry, but lacks an automated way to prioritize which physical machines need immediate field technician intervention based on real-time temperature anomalies and battery decay.

### The Airflow Solution
We will manually deploy a new DAG (`manual_sensor_maintenance_classifier`) that reads raw telemetry, runs risk classification algorithms, and populates an actionable **Maintenance Queue** table (`sensor_maintenance_queue`) in PostgreSQL.

---

## 🔍 Before vs. After State Comparison

| Dimension | BEFORE DAG Enablement | AFTER DAG Enablement |
| :--- | :--- | :--- |
| **`sensor_maintenance_queue` Table State** | Empty (0 rows) | Populated with 9 categorized maintenance tickets |
| **Hardware Risk Classification** | Unknown / Manual inspection required | Automatically scored (`CRITICAL`, `HIGH`, `MEDIUM`, `NORMAL`) |
| **Field Action Recommendations** | None | Specific maintenance instructions assigned per device |
| **Airflow UI Status** | DAG not present / Unpaused | DAG `manual_sensor_maintenance_classifier` -> `SUCCESS` |

---

## 🛠️ Step-by-Step Exercise Instructions

### Step 1: Verify the BEFORE State (Database Query)
Before deploying the DAG, verify that no maintenance tickets exist in the database.

On your host terminal:
```bash
docker exec -it iot_telemetry_db psql -U iot_user -d iot_telemetry -c "TABLE sensor_maintenance_queue;"
```

---

### Step 2: Initialize Maintenance Table Schema
Run `init_maintenance_schema.sql` to create the target table in PostgreSQL:

```bash
cd airflow/04_manual_dag_exercise
docker exec -i iot_telemetry_db psql -U iot_user -d iot_telemetry < init_maintenance_schema.sql
```

Re-query the database:
```bash
docker exec -it iot_telemetry_db psql -U iot_user -d iot_telemetry -c "TABLE sensor_maintenance_queue;"
```
*(Result: Table created, `0 rows` present).*

---

### Step 3: Deploy the New DAG File to Airflow
Copy `manual_sensor_cleaning_dag.py` into the Airflow DAG mounting folder (`01_install/dags/`):

```bash
cp dags/manual_sensor_cleaning_dag.py ../01_install/dags/
```

---

### Step 4: Enable and Trigger the DAG in Airflow UI
1. Open your browser to Airflow UI: **[http://localhost:8080](http://localhost:8080)** *(or `http://<HOST_IP>:8080` for remote host access)*
2. In the DAG list, locate **`manual_sensor_maintenance_classifier`**.
3. Toggle the switch next to the DAG name from **OFF** to **ON** (Unpause).
4. Click the **Play / Trigger DAG** button.
5. Click on `manual_sensor_maintenance_classifier` -> **Graph View** to watch the TaskFlow tasks transition to green (`SUCCESS`):
   - `extract_telemetry_for_maintenance` ➔ `classify_device_risk` ➔ `populate_maintenance_queue`

---

### Step 5: Verify the AFTER State (Database Query)
Query the database table again to showcase the populated maintenance tickets:

```bash
docker exec -it iot_telemetry_db psql -U iot_user -d iot_telemetry -c "SELECT ticket_id, device_id, current_temp, risk_level, priority_score, recommended_action FROM sensor_maintenance_queue ORDER BY priority_score DESC;"
```

**Expected AFTER Output:**
```text
 ticket_id |   device_id    | current_temp | risk_level | priority_score |                          recommended_action                          
-----------+----------------+--------------+------------+----------------+----------------------------------------------------------------------
         9 | IOT-NODE-GAMMA |        89.10 | CRITICAL   |            100 | CRITICAL DISPATCH: Emergency Cooling Unit Replacement Required
         3 | IOT-NODE-ALPHA |        82.50 | CRITICAL   |            100 | CRITICAL DISPATCH: Emergency Cooling Unit Replacement Required
         8 | IOT-NODE-GAMMA |        78.40 | HIGH       |             75 | HIGH PRIORITY: HVAC Filter & Duct Inspection
         4 | IOT-NODE-GAMMA |        65.00 | NORMAL     |             10 | ROUTINE MONITORING: System Nominal
         1 | IOT-NODE-ALPHA |        22.40 | NORMAL     |             10 | ROUTINE MONITORING: System Nominal
(9 rows)
```
