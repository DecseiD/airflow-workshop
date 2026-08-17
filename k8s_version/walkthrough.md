# Walkthrough (AKS)

Use this as your execution log while running the workshop in Kubernetes.

## 1) Context + namespace checks

```bash
kubectl config current-context
kubectl get ns
```

## 2) Airflow deployment checks

```bash
helm ls -n airflow
kubectl get pods -n airflow
kubectl get svc -n airflow
```

## 3) Azure Entra ID SSO checks

- Open Airflow URL from Ingress
- Confirm **Login with Azure/Entra** button appears
- Confirm successful redirect/callback

## 4) ETL stack checks

```bash
kubectl get pods -n airflow -l app=iot-telemetry-db
kubectl get pods -n airflow -l app=iot-api
kubectl get pods -n airflow -l app=airflow-dashboard
kubectl get ingress -n airflow
```

## 5) API checks

```bash
curl -sS http://<api-host>/api/health
curl -sS http://<api-host>/api/metrics
curl -sS http://<api-host>/api/alerts
```

## 6) Airflow DAG checks

- DAG `iot_telemetry_etl` is visible and successful.
- DAG `manual_sensor_maintenance_classifier` is visible and successful.

## 7) Dashboard checks

- Dashboard loads.
- Raw log panel populates.
- Metrics + Alerts panels do not show `API unavailable`.
- Maintenance queue appears after Module 04 DAG run.

## 8) Module 05 git-based DAG retrieval checks

```bash
helm upgrade --install airflow apache-airflow/airflow \
  -n airflow \
  -f 01_install/values-airflow.yaml \
  -f 05_git_based_dag_retrieval/values-git-sync.yaml

kubectl logs -n airflow deploy/airflow-scheduler -c git-sync --tail=200
kubectl exec -n airflow deploy/airflow-scheduler -c scheduler -- airflow dags list
```

Expected:
- `git-sync` shows successful sync cycles and commit updates.
- DAGs from the configured Git repo appear in Airflow without manual `kubectl cp`.
