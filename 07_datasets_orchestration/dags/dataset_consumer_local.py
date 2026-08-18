from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.datasets import Dataset
from airflow.decorators import task

DATASET_TELEMETRY_CLEANED = Dataset("dataset://iot/telemetry/cleaned")
PAYLOAD_PATH = Path("/opt/airflow/dags/07_datasets_orchestration/data/cleaned_telemetry_latest.json")


with DAG(
    dag_id="dataset_arrival_consumer_local",
    description="Module 07 consumer: runs automatically on dataset updates",
    start_date=datetime(2025, 1, 1),
    schedule=[DATASET_TELEMETRY_CLEANED],
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(seconds=30)},
    tags=["module07", "datasets", "local"],
) as dag:

    @task(task_id="consume_dataset_update")
    def consume_dataset_update() -> str:
        if not PAYLOAD_PATH.exists():
            return f"No payload file found at {PAYLOAD_PATH}. Producer may not have run yet."

        payload = json.loads(PAYLOAD_PATH.read_text(encoding="utf-8"))
        dataset_uri = payload.get("dataset_uri", "unknown")
        updated_at = payload.get("updated_at_utc", "unknown")
        mode = payload.get("mode", "unknown")

        return (
            "Consumer triggered by dataset update. "
            f"dataset_uri={dataset_uri}, updated_at_utc={updated_at}, mode={mode}"
        )

    consume_dataset_update()
