# 02_usecase_etl — IoT ETL on AKS

Deploy PostgreSQL telemetry DB, Flask API, and dashboard into AKS.

## 1) Images

Current manifests are using prebuilt images:
- API: `cheesecakeslice/airflow-workshop:v1.0`
- Dashboard: `cheesecakeslice/airflow-dashboard:latest`

If you want to use your own images, build/push first and then update image fields in:
- `k8s/iot-api-deployment.yaml`
- `k8s/dashboard-deployment.yaml`

```bash
# API image
docker build -t <registry>/iot-api:latest ./api
docker push <registry>/iot-api:latest

# Dashboard image
docker build -t <registry>/airflow-dashboard:latest ./dashboard
docker push <registry>/airflow-dashboard:latest
```

## 2) Apply manifests

```bash
kubectl apply -n airflow -f k8s/postgres-configmap.yaml
kubectl apply -n airflow -f k8s/postgres-statefulset.yaml
kubectl apply -n airflow -f k8s/postgres-service.yaml

kubectl apply -n airflow -f k8s/iot-api-deployment.yaml
kubectl apply -n airflow -f k8s/iot-api-service.yaml

kubectl apply -n airflow -f k8s/dashboard-deployment.yaml
kubectl apply -n airflow -f k8s/dashboard-service.yaml
kubectl apply -n airflow -f k8s/ingress.yaml
```

## 3) Workshop demo access (port-forward, recommended)

For workshop reliability, use local port-forward instead of host-based ingress.

In two terminals:

```bash
kubectl port-forward -n airflow svc/airflow-dashboard 8081:80
kubectl port-forward -n airflow svc/iot-api 5000:5000
```

Open dashboard with explicit API override:

```text
http://localhost:8081/?api=http://localhost:5000
```

This avoids DNS/host-file/ingress-controller dependencies during the demo.

### Optional alternative: ingress host mapping

If you prefer host-based ingress, map these hosts to your ingress/LB IP:

```text
<INGRESS_OR_LB_IP> api.local
<INGRESS_OR_LB_IP> dashboard.local
```

## 4) Deploy DAG to Airflow

Option A (recommended): keep `dags/minimal_etl.py` in your DAG source repo and let your sync mechanism (for example, Module 05 git-sync) deliver it.

Option B: direct copy for lab demo:

```bash
SCHED=$(kubectl get pod -n airflow -l component=scheduler -o jsonpath='{.items[0].metadata.name}')
kubectl cp dags/minimal_etl.py airflow/$SCHED:/opt/airflow/dags/minimal_etl.py
```

## 5) Verify workloads + endpoints

```bash
kubectl get pods -n airflow
kubectl get svc -n airflow
curl -sS http://localhost:5000/api/health
```

Expected:
- API health returns `{"status":"ok"}`
- Dashboard reachable with API override at `http://localhost:8081/?api=http://localhost:5000`

## 6) Insert sample data

`add_sensor_data.py` is configured for local DB access (`localhost:5433`), so port-forward Postgres first:

```bash
kubectl port-forward -n airflow svc/iot-telemetry-db 5433:5432
python add_sensor_data.py --anomaly
```

## 7) Run demo flow

1. Trigger DAG `iot_telemetry_etl` in Airflow UI.
2. Open dashboard: `http://localhost:8081/?api=http://localhost:5000`
3. Validate raw/metrics/alerts panels update.

## 8) Troubleshooting notes from working AKS run

### A) Dashboard shows `API unavailable`

Root cause in this module: dashboard JS defaults API base to:

```text
${window.location.protocol}//${window.location.hostname}:5000
```

If dashboard is opened on `dashboard.local`, that points to `dashboard.local:5000` (wrong target for API).

Use one of these:
- Preferred (workshop): local port-forward override:
  - `http://localhost:8081/?api=http://localhost:5000`
- Optional host-based ingress override:
  - `http://dashboard.local/?api=http://api.local`
  - `http://dashboard.local/?api=http://<api-reachable-host>:5000`

### B) Pods healthy but URLs fail

For workshop mode, verify both port-forwards are running (`8081->dashboard`, `5000->iot-api`).

For ingress mode, this is usually missing host mapping for ingress hosts (`api.local`, `dashboard.local`).

### C) Data does not appear after API is healthy

Run data insert + DAG trigger again:
- `python add_sensor_data.py --anomaly`
- Trigger `iot_telemetry_etl`
