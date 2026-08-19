# Module 06: Monitoring Airflow on AKS (Workshop Lightweight)

This optional module adds a lightweight monitoring layer for the AKS workshop:

- Airflow metrics via **StatsD exporter** (Airflow Helm chart)
- Cluster metrics via **kube-prometheus-stack** (Prometheus + Grafana)
- Minimal dashboard focus for workshop demos

---

## 1) Deploy monitoring stack

```bash
# Add/update Helm repos
helm repo add apache-airflow https://airflow.apache.org
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Ensure Airflow emits metrics through statsd-exporter
helm upgrade --install airflow apache-airflow/airflow \
  -n airflow \
  -f ../01_install/values-airflow.yaml \
  -f values-airflow-monitoring.yaml

# Deploy lightweight Prometheus+Grafana stack
helm upgrade --install workshop-monitoring prometheus-community/kube-prometheus-stack \
  -n airflow \
  -f values-kube-prometheus-stack.yaml
```

---

## 2) Access Grafana

```bash
kubectl port-forward -n airflow svc/workshop-monitoring-grafana 3002:80
```

Open: `http://localhost:3002`

Credentials (from values file defaults):
- user: `admin`
- password: `admin`

---

## 3) Verification checks

```bash
kubectl get pods -n airflow | grep -E "statsd|prometheus|grafana"
kubectl get servicemonitor -n airflow
kubectl logs -n airflow deploy/airflow-scheduler --tail=200
```

Expected:
- Airflow scheduler emits metrics to statsd-exporter
- Prometheus targets include Airflow statsd metrics endpoint
- Grafana dashboards can query Prometheus datasource

---

## 4) Workshop demo path (10–12 minutes)

1. Trigger DAG `iot_telemetry_etl`.
2. Show task success/failure counters in Grafana.
3. Show scheduler heartbeat/processing metrics.
4. Explain how this expands into full alerting (Alertmanager) post-workshop.

---

## 5) Why this is workshop-lightweight

- Single namespace deployment (`airflow`)
- Minimal retention and disabled heavy defaults
- No custom TSDB/long-term storage setup
- Focused on observability fundamentals, not full SRE platform depth
