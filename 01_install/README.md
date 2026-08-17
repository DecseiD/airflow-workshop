# Module 01: Apache Airflow Setup (Local Docker Compose)

Welcome to Module 01. In this section, you set up a multi-container Apache Airflow 2.10.x environment on your local lab host using Docker Compose.

---

## 1. Architecture Overview

| Service / Container | Role |
| :--- | :--- |
| **`airflow_postgres`** | Metadata database (PostgreSQL 15) |
| **`airflow_init`** | Transient initializer: migrations + admin user bootstrap |
| **`airflow_webserver`** | Airflow UI on port `8080` |
| **`airflow_scheduler`** | Schedules and dispatches DAG runs |
| **`airflow_triggerer`** | Async event loop for deferred tasks |

> Resource note: memory limits are intentionally set in `docker-compose.yaml` for single-host stability.

---

## 2. Prerequisites & Environment Setup

- Linux host / VM / workstation
- Docker Engine + Docker Compose v2
- Shell access (local terminal or SSH)

### Step 1: Navigate to module folder
```bash
cd airflow/01_install
```

### Step 2: Prepare mounts and UID mapping
```bash
mkdir -p dags logs plugins config
echo "AIRFLOW_UID=$(id -u)" > .env
```

---

## 3. Launch Apache Airflow

### Step 3: Initialize DB and admin account
```bash
docker compose up airflow-init
```

Expected completion includes successful DB migration and admin creation.

### Step 4: Start core services
```bash
docker compose up -d
```

### Step 5: Verify health
```bash
docker compose ps
```

Expected services: `postgres`, `airflow-webserver`, `airflow-scheduler`, `airflow-triggerer` healthy.

---

## 4. Access Airflow UI

- **URL:** [http://localhost:8080](http://localhost:8080)
- **Credentials:**
  - Username: `admin`
  - Password: `admin`

If running on a remote host, use `http://<HOST_IP>:8080`.

---

## 5. Helpful CLI Commands

```bash
# stream all logs
docker compose logs -f

# resource usage
docker stats airflow_webserver airflow_scheduler airflow_postgres

# Trigger DAG reserialization. Might require UI restart.
docker compose exec airflow-scheduler airflow dags reserialize

# airflow CLI
docker compose exec airflow-webserver airflow dags list

# stop services
docker compose stop
```

---

## 6. Next Step
Proceed to `../02_usecase_etl` to deploy the IoT database, API, and dashboard.
