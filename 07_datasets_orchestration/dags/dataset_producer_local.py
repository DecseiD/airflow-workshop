from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from airflow import DAG
from airflow.datasets import Dataset
from airflow.decorators import task

DATASET_TELEMETRY_CLEANED = Dataset("dataset://iot/telemetry/cleaned")
PAYLOAD_PATH = Path("/opt/airflow/dags/07_datasets_orchestration/data/cleaned_telemetry_latest.json")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


with DAG(
    dag_id="dataset_arrival_producer_local",
    description="Module 07 producer: emit dataset event when cleaned telemetry arrives",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(seconds=30)},
    tags=["module07", "datasets", "local"],
) as dag:

    @task(task_id="publish_cleaned_telemetry_dataset", outlets=[DATASET_TELEMETRY_CLEANED])
    def publish_cleaned_telemetry_dataset() -> str:
        PAYLOAD_PATH.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "dataset_uri": str(DATASET_TELEMETRY_CLEANED.uri),
            "event_type": "data_arrived",
            "updated_at_utc": _utc_now_iso(),
            "mode": "overwrite",
            "source": "module07_local_demo",
        }

        PAYLOAD_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return f"Dataset event published and payload overwritten at {PAYLOAD_PATH}"

    publish_cleaned_telemetry_dataset()
