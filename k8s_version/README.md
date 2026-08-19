# Apache Airflow Workshop (AKS / Kubernetes Version)

This folder provides the **Kubernetes (AKS) equivalent** of the local Docker workshop.
It keeps the same learning structure and ETL logic, but deploys Airflow and workshop apps into an existing AKS cluster.

> Scope: **cluster already exists**. This guide does **not** include AKS cluster creation.

## Structure

- `01_install/` — Airflow on AKS (Helm) + Azure Entra ID SSO
- `02_usecase_etl/` — IoT ETL use case (DB, DAG, API, dashboard)
- `04_manual_dag_exercise/` — Manual DAG exercise for maintenance queue classification
- `05_git_based_dag_retrieval/` — Git-based DAG delivery workflow (production-like)
- `06_monitoring_airflow/` — Lightweight Airflow monitoring on AKS (Prometheus + Grafana)
- `03_operational_painpoints/` — Capstone production troubleshooting on Kubernetes
- `walkthrough.md` — end-to-end run/verification log

## Quick start (high-level)

1. Configure kubectl context to your existing AKS cluster.
2. Deploy Airflow with Helm using `01_install/values-airflow.yaml`.
3. Access Airflow UI via webserver `LoadBalancer` external IP (or ingress, if configured).
4. Configure Airflow Web UI SSO via Azure Entra ID secrets + redirect URI (`/oauth-authorized`).
5. Deploy IoT DB/API/dashboard manifests from `02_usecase_etl/k8s/`, then run Module 02 with port-forward (`localhost:8081` dashboard + `localhost:5000` API) for workshop-stable access.
6. Add `iot_db_conn` in Airflow and trigger the DAGs.
7. Run Module 04 manual DAG exercise.
8. Enable Module 05 git-based DAG retrieval flow for production-like delivery behavior.
9. Enable Module 06 monitoring stack for Airflow metrics visibility.
10. Use Module 03 as final troubleshooting capstone.

See module READMEs for exact commands.
