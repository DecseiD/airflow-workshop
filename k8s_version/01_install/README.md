# 01_install — Airflow on AKS + Azure Entra ID SSO

This module deploys Airflow on an existing AKS cluster with Helm and enables Azure Entra ID (OIDC/OAuth) login for the Airflow UI.

## Prerequisites

- Existing AKS cluster and working `kubectl` context
- Helm v3
- NGINX ingress controller (or compatible ingress class)
- Azure Entra app registration for Airflow UI login

## 1) Create namespace + secrets

```bash
kubectl apply -f manifests/namespace.yaml

kubectl -n airflow create secret generic airflow-entra-auth \
  --from-literal=AZURE_TENANT_ID='<tenant-id>' \
  --from-literal=AZURE_CLIENT_ID='<client-id>' \
  --from-literal=AZURE_CLIENT_SECRET='<client-secret>'
```

## 2) Add Helm repo and deploy Airflow

```bash
helm repo add apache-airflow https://airflow.apache.org
helm repo update

helm upgrade --install airflow apache-airflow/airflow \
  -n airflow \
  -f values-airflow.yaml
```

## 3) Validate pods

```bash
kubectl get pods -n airflow
kubectl get ingress -n airflow
```

## 4) Azure Entra ID redirect URI

Configure your Entra app redirect URI to:

```text
https://airflow.local/oauth-authorized
```

This follows the official FAB SSO guide for Airflow provider auth manager.

Replace `airflow.local` with your chosen Airflow host in `values-airflow.yaml` ingress config.

## 5) Airflow connection for ETL DB

After Module 02 DB is deployed, set connection env via Helm values (already included):

- `AIRFLOW_CONN_IOT_DB_CONN=postgresql://iot_user:iot_password@iot-telemetry-db.airflow.svc.cluster.local:5432/iot_telemetry`

If you change service name/namespace, update this URI.
