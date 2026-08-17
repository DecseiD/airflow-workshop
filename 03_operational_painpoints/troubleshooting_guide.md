# Production Field Guide: Airflow Operational Pain Points (Single-Host Lab)

This guide addresses critical operational failure modes, performance bottlenecks, developer friction, and security considerations when running Apache Airflow on host.

---

## 1. Single-Host Operational Considerations

Running Airflow alongside other host containers on a single node introduces specific infrastructure constraints.

### 1.1 Strictly Respecting Host Swap Constraints (4 GB Swap Limit)
* **Risk:** If host swap is strictly capped at **4 GB**, unconstrained memory growth in Airflow workers/scheduler can trigger Linux OOM kills and destabilize the host.
* **Mitigation:** Always declare container memory limits in `docker-compose.yaml` using `deploy.resources.limits.memory`. Never run Airflow containers without explicit memory caps on a single host.

---

## 2. UI & Scheduler Dysfunction

### Problem 2.1: DAGs Do Not Appear in the UI
One of the most common issues for data engineers is deploying a DAG file that fails to render in the web interface.

#### Root Causes:
1. **Python Import / Syntax Errors:** Top-level Python exceptions prevent `DagBag` from parsing the file.
2. **`.airflowignore` Exclusions:** The file path matches a pattern listed in `.airflowignore`.
3. **DAG Parsing Timeouts:** The DAG file takes longer than `dagbag_import_timeout` (default 30s) to execute top-level code.
4. **Missing Airflow Objects:** The file does not contain an instantiated `DAG` object or `@dag` decorated function.

#### Diagnostics & Remediation:
Run the import error check CLI command inside the scheduler container:
```bash
docker compose exec airflow-scheduler airflow dags list-import-errors
```
* **Fixing Top-Level Code Overhead:** Never execute external API calls or database queries at the top level of a DAG file. Keep top-level code lightweight:

```python
# ❌ BAD PRACTICE: Executes query every time the Scheduler parses the file (every 10 seconds)
from airflow.providers.postgres.hooks.postgres import PostgresHook
db_records = PostgresHook('my_db').get_records("SELECT * FROM configuration_table")

# ✅ GOOD PRACTICE: Move heavy calls inside the task execution context
@task
def fetch_config():
    return PostgresHook('my_db').get_records("SELECT * FROM configuration_table")
```

---

### Problem 2.2: Scheduler Heartbeat Failures & Zombie Tasks
Tasks get stuck in `queued` or `scheduled` state, or the UI displays a warning banner stating *"The scheduler does not appear to be running."*

#### Root Causes:
* **Database Deadlocks / Resource Exhaustion:** The metadata database is throttled, delaying scheduler state updates.
* **OOM (Out Of Memory) Kills:** The scheduler process was terminated by the kernel OOM killer due to host RAM pressure.
* **Zombie Tasks:** Workers abruptly lose network connectivity or crash without updating task state in Postgres.

#### Diagnostics & Remediation:
1. Check scheduler process health on the host:
   ```bash
   docker compose exec airflow-scheduler airflow jobs check --job-type SchedulerJob --hostname "$HOSTNAME"
   ```
2. Adjust zombie detection timeout settings in environment variables:
   ```env
   AIRFLOW__SCHEDULER__SCHEDULER_ZOMBIE_TASK_THRESHOLD=300
   AIRFLOW__SCHEDULER__JOB_HEARTBEAT_SEC=15
   ```

---

### Problem 2.3: Database Connection Errors & Pool Exhaustion
Error logs report `sqlalchemy.exc.TimeoutError: QueuePool limit of size 5 overflow 10 reached` or `psycopg2.OperationalError: FATAL: remaining connection slots are reserved`.

#### Root Causes:
Each Airflow component (webserver, scheduler, triggerer, workers) opens multiple persistent SQLAlchemy connections. Uncapped parallel tasks exhaust Postgres `max_connections`.

#### Remediation & Tuning:
1. **Tune Connection Pool Settings:**
   ```env
   AIRFLOW__DATABASE__SQL_ALCHEMY_POOL_SIZE=10
   AIRFLOW__DATABASE__SQL_ALCHEMY_MAX_OVERFLOW=20
   ```
2. **Deploy PgBouncer:** Use a lightweight connection pooler in front of PostgreSQL for production deployments.

---

## 3. Developer Experience & The "Sync Tax"

### The "Sync Tax" Pain Point
In remote Kubernetes environments, developers modify code locally, commit to Git, wait for `git-sync` sidecars (30s-120s polling interval), and reload the UI. This **Sync Tax** severely degrades velocity.

```text
[Local Code Change] ---> [Git Commit/Push] ---> [CI Pipeline] ---> [Git-Sync Poll (60s)] ---> [Airflow Parse] ---> [UI Test]
                                 ⏱️ Total Wait Time: 3 to 5 Minutes Per Iteration ⏱️
```

### Mitigations & Fast Feedback Loops
1. **Local Direct Editing:** Edit code directly in mounted `/opt/airflow/dags` volumes for instant DAG refresh.
2. **Instant CLI DAG Testing:** Test task execution directly on the host without triggering a full DAG run:
   ```bash
   # Test a single task locally bypassing scheduler and metadata DB writes
   docker compose exec airflow-scheduler airflow tasks test iot_telemetry_etl extract_raw_telemetry 2026-08-14
   ```

---

## 4. Webserver Performance & 502/504 Gateway Errors

### Problem: Webserver Overload Under Load
Users experience `502 Bad Gateway` or `504 Gateway Timeout` errors when accessing the UI during live presentations or peak workflow execution.

#### Root Causes:
1. **Gunicorn Worker Starvation:** Default Gunicorn worker count (`4`) is insufficient for concurrent presentation clients.
2. **UI Parsing Heavy DAG Bags:** The webserver loads and parses DAG files directly to render DAG details and code views.

#### Remediation & Production Configuration:

```env
# 1. Tune Gunicorn sync workers based on available host CPU cores
AIRFLOW__WEBSERVER__WEB_SERVER_WORKERS=4

# 2. Increase worker refresh and timeout limits
AIRFLOW__WEBSERVER__WEB_SERVER_MASTER_TIMEOUT=120
AIRFLOW__WEBSERVER__WEB_SERVER_WORKER_TIMEOUT=120

# 3. Enable worker preloading to share memory across Gunicorn forks
AIRFLOW__WEBSERVER__WORKER_REFRESH_INTERVAL=1800
```

---

## 5. Advanced Known-Issues Appendix

For additional workshop scenarios imported from external field notes, see:
- [`known_issues.md`](./known_issues.md)

This appendix covers deeper Kubernetes-oriented edge cases, including:
- OOM kill / zombie-task behavior
- API-server overload patterns
- Triggerer loop starvation
- PVC multi-attach anomalies
- autoscaling graceful-shutdown failures

---

## 6. Security Vulnerabilities & Log Volume Isolation

### Critical Vulnerability Context: CVE-2025-66236 & Shared Log Exploits
In multi-tenant Airflow clusters where multiple teams share worker nodes or log directories, shared file system permissions pose high-security risks.

#### Attack Vectors (Read & Write Path Attacks):
1. **Read-Path Attacks:** A user creating DAGs in Team A crafts a Python task that reads local log folders (`/opt/airflow/logs`) belonging to Team B's DAG runs, exposing sensitive API credentials or tokens printed in logs.
2. **Write-Path Attacks (e.g. CVE-2025-66236):** Malicious DAG tasks write symlinks or exploit log endpoints to write payload scripts into webserver-accessible file paths.

#### Security Best Practices & Isolation Rules:
1. **Enforce Remote Logging:** Ship task logs directly to AWS S3, Google Cloud Storage, or Elasticsearch instead of persistent local shared worker disks.
2. **Mount Log Directories as Read-Only for Webserver:** Mount worker log paths into the webserver container with strict read-only flags (`:ro`) and unprivileged container users (`user: 50000:0`).
3. **Use KubernetesExecutor with Isolated Namespaces:** Run tasks in isolated Pods and Kubernetes Namespaces with dedicated IAM roles.
