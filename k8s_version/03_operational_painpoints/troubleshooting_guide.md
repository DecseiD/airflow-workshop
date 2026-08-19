# Airflow on AKS — Troubleshooting Guide

## 1. DAG not showing in UI

```bash
kubectl logs -n airflow deploy/airflow-scheduler --tail=200
kubectl exec -n airflow deploy/airflow-scheduler -- airflow dags list-import-errors
```

Common causes:
- syntax/import errors in DAG file
- DAG file not present in scheduler container
- missing Python dependency in Airflow image

## 2. Scheduler heartbeat / stuck tasks

```bash
kubectl get pods -n airflow
kubectl logs -n airflow deploy/airflow-scheduler --tail=200
kubectl describe pod -n airflow -l component=scheduler
```

## 3. Web UI 502/504 (optional ingress-only scenario)

```bash
kubectl describe ingress -n airflow
kubectl logs -n ingress-nginx deploy/ingress-nginx-controller --tail=200
kubectl top pods -n airflow
```

Mitigations:
- increase webserver replicas
- tune gunicorn/webserver workers
- increase ingress/proxy timeouts

## 4. Entra SSO login fails

Checklist:
- redirect URI matches Airflow host + `/oauth-authorized`
- tenant/client id/secret are correct in `airflow-entra-auth`
- webserver config loaded and pod restarted

```bash
kubectl get secret airflow-entra-auth -n airflow
kubectl rollout restart deploy/airflow-webserver -n airflow
kubectl logs -n airflow deploy/airflow-webserver --tail=200
```

## 5. ETL API shows "API unavailable"

```bash
kubectl logs -n airflow deploy/iot-api --tail=200
kubectl exec -n airflow deploy/iot-api -- wget -qO- http://localhost:5000/api/health
```

Validate schema/columns alignment:
- metrics timestamp source: `daily_sensor_metrics.calculated_at`
- alerts timestamp source: `sensor_alerts.alert_timestamp`

## 6. Advanced known-issues appendix

For imported AKS-focused operational edge cases (OOM/zombies, Triggerer starvation, PgBouncer bottlenecks, multi-attach storage errors, KEDA shutdown behavior), review:
- `known_issues.md`
