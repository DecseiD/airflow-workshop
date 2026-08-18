# Module 07: Dataset-Driven Orchestration (Local)

This module demonstrates Airflow **Datasets** with a short producer/consumer flow.

- Producer DAG marks dataset update when data arrives.
- Consumer DAG triggers automatically from that dataset event.

Dataset URI used in this workshop:

- `dataset://iot/telemetry/cleaned`

---

## 1) DAG availability assumption

If Module 05 git-sync is enabled, these DAGs are already synced from the repo.
No manual copy step is required.

---

## 2) Validate DAG visibility

From `01_install/`:

```bash
docker compose exec airflow-webserver airflow dags list | grep -E "dataset_arrival_(producer|consumer)_local"
```

Expected:
- `dataset_arrival_producer_local`
- `dataset_arrival_consumer_local`

---

## 3) Run short demo

1. In Airflow UI, trigger `dataset_arrival_producer_local`.
2. Open **Datasets** tab and confirm dataset event update:
   - `dataset://iot/telemetry/cleaned`
3. Confirm `dataset_arrival_consumer_local` is triggered by dataset event.

---

## 4) Notes

- Duplicate data arrival is modeled as overwrite (latest payload wins).
- Failure handling is via DAG/task retries.
- This module is intentionally short and demo-focused.
