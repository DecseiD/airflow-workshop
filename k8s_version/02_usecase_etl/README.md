# 02_usecase_etl — IoT ETL on AKS

Deploy a PostgreSQL telemetry DB, Flask API, and dashboard into AKS.

## 1) Build and push images

Use your own registry and tag convention.

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

## 3) Deploy DAG to Airflow

Option A (recommended for workshop): place `dags/minimal_etl.py` into your Airflow DAG source so your sync mechanism (for example, git-sync) delivers it to scheduler/webserver pods.

Option B: copy directly into scheduler/webserver pods for lab demo:

```bash
SCHED=$(kubectl get pod -n airflow -l component=scheduler -o jsonpath='{.items[0].metadata.name}')
kubectl cp dags/minimal_etl.py airflow/$SCHED:/opt/airflow/dags/minimal_etl.py
```

## 4) Verify

```bash
kubectl get pods -n airflow
kubectl get ingress -n airflow
curl -sS http://api.local/api/health
```

## 5) Run demo flow

1. Insert data: `python add_sensor_data.py --anomaly`
2. Trigger DAG `iot_telemetry_etl` in Airflow UI.
3. Open dashboard (`http://dashboard.local`) and verify raw/metrics/alerts panels.
