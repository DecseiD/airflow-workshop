# Module 06: Monitoring Airflow (Lightweight + Workshop-Friendly)

This module adds a **balanced monitoring stack** for the local lab:

- **StatsD Exporter** (collect Airflow metrics)
- **Prometheus** (scrape + store metrics)
- **Grafana** (dashboards)

Goal: keep setup lightweight while still demonstrating production-style observability.

---

## 1) Architecture for this module

```text
Airflow (webserver/scheduler/triggerer)
        -> StatsD metrics (UDP 9125)
        -> statsd-exporter (:9102)
        -> Prometheus (:9090)
        -> Grafana (:3002)
```

---

## 2) Start monitoring stack

From `airflow-workshop/01_install` run:

```bash
docker compose \
  -f docker-compose.yaml \
  -f ../06_monitoring_airflow/docker-compose.monitoring.yaml \
  up -d
```

This command both:
- keeps Airflow core services
- injects metrics env vars into Airflow services
- starts `statsd-exporter`, `prometheus`, `grafana`

---

## 3) Access URLs

- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3002`
  - user: `admin`
  - password: `admin`

---

## 4) Quick verification

```bash
# metrics endpoint exposed by statsd-exporter
curl -sS http://localhost:9102/metrics | head

# Prometheus targets should be UP
curl -sS http://localhost:9090/api/v1/targets
```

In Grafana, open dashboard: **Airflow Workshop Overview**.

---

## 5) What to demonstrate live

1. Trigger `iot_telemetry_etl` in Airflow.
2. Open Grafana dashboard.
3. Show scheduler heartbeat metric trend and DAG/task counters.
4. Explain alerting candidate metrics (scheduler stalls, task failures).

---

## 6) Lightweight design decisions

- No long-retention TSDB tuning (workshop runtime only).
- No Alertmanager dependency in local module.
- Single Prometheus + single Grafana instance.

Use Module 03 (capstone) for deeper production troubleshooting discussion.
