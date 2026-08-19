# Apache Airflow Workshop (AKS / Kubernetes Version)

This folder provides the **Kubernetes (AKS) equivalent** of the local Docker workshop.
It keeps the same learning structure and ETL logic, but deploys Airflow and workshop apps into an existing AKS cluster.

> Scope: **cluster already exists**. This guide does **not** include AKS cluster creation.

## Structure

- `01_install/` — Airflow on AKS (Helm) + Azure Entra ID SSO
- `02_usecase_etl/` — IoT ETL use case (DB, DAG, API, dashboard)
- `04_manual_dag_exercise/` — Manual DAG exercise for maintenance queue classification
- `05_git_based_dag_retrieval/` — Optional automatic DAG sync workflow
- `06_monitoring_airflow/` — Lightweight Airflow monitoring on AKS (Prometheus + Grafana)
- `03_operational_painpoints/` — Optional capstone troubleshooting module
- `walkthrough.md` — end-to-end run/verification log

## Quick start (high-level)

1. Configure kubectl context to your existing AKS cluster.
2. Deploy Airflow with Helm using `01_install/values-airflow.yaml`.
3. Open Airflow UI on webserver `LoadBalancer` IP and verify Entra SSO login.
4. Deploy IoT DB/API/dashboard manifests from `02_usecase_etl/k8s/`.
5. Run Module 02 with port-forward (`localhost:8081` dashboard + `localhost:5000` API).
6. Add `iot_db_conn` in Airflow and trigger the DAGs.
7. Run Module 04 manual DAG exercise.
8. (Optional) Enable Module 05 git-based DAG sync.
9. (Optional) Enable Module 06 monitoring stack.
10. (Optional) Use Module 03 troubleshooting capstone.

See module READMEs for exact commands.
