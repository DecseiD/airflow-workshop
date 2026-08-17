"""
===============================================================================
DAG Name: iot_telemetry_etl
Description: Production-ready IoT Sensor Telemetry ETL pipeline utilizing
             Airflow TaskFlow API (@dag, @task) and PostgresHook.
===============================================================================
"""

from datetime import datetime, timedelta
import logging
from typing import Dict, List, Any

from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook

# Default configuration parameters for the DAG
DEFAULT_ARGS = {
    'owner': 'data_engineering_team',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
}

# Temperature threshold for anomaly alerts (in Celsius)
CRITICAL_TEMP_THRESHOLD = 75.0
POSTGRES_CONN_ID = 'iot_db_conn'


@dag(
    dag_id='iot_telemetry_etl',
    default_args=DEFAULT_ARGS,
    description='ETL pipeline for ingesting, transforming, and alerting on IoT sensor telemetry',
    schedule_interval='@hourly',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['workshop', 'etl', 'taskflow', 'iot'],
)
def iot_telemetry_etl_pipeline():
    """
    Main TaskFlow API DAG pipeline definition for IoT Telemetry processing.
    """

    @task(task_id='extract_raw_telemetry')
    def extract_telemetry() -> List[Dict[str, Any]]:
        """
        Extract Step: Connects to PostgreSQL database via PostgresHook
        and queries all unprocessed sensor readings.
        """
        logging.info("Initializing PostgresHook connection: %s", POSTGRES_CONN_ID)
        pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)

        sql = """
            SELECT reading_id, device_id, location, temperature_celsius, 
                   humidity_pct, battery_pct, reading_timestamp
            FROM raw_sensor_readings
            WHERE processed = FALSE;
        """
        
        # Execute query and extract records as list of dictionaries
        conn = pg_hook.get_conn()
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        colnames = [desc[0] for desc in cursor.description]
        records = [dict(zip(colnames, row)) for row in rows]
        
        cursor.close()
        conn.close()

        logging.info("Extracted %d unprocessed telemetry records.", len(records))
        return records

    @task(task_id='transform_telemetry')
    def transform_telemetry(records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Transform Step: 
        1. Aggregates min, max, average temperatures per device and date.
        2. Detects high-temperature threshold anomalies (>75°C).
        3. Prepares record IDs for state updates.
        """
        if not records:
            logging.info("No new records to transform.")
            return {"aggregated_metrics": [], "alerts": [], "processed_ids": []}

        device_aggregates: Dict[str, Dict[str, Any]] = {}
        alerts: List[Dict[str, Any]] = []
        processed_ids: List[int] = []

        for record in records:
            r_id = record['reading_id']
            dev_id = record['device_id']
            loc = record['location']
            temp = float(record['temperature_celsius'])
            ts = record['reading_timestamp']
            
            # Format date string for aggregation key
            date_str = str(ts).split(' ')[0] if hasattr(ts, 'strftime') else str(ts)[:10]
            key = f"{dev_id}_{date_str}"

            processed_ids.append(r_id)

            # 1. Anomaly Detection Logic
            if temp > CRITICAL_TEMP_THRESHOLD:
                severity = 'CRITICAL' if temp > 90.0 else 'WARNING'
                alerts.append({
                    'reading_id': r_id,
                    'device_id': dev_id,
                    'alert_type': 'HIGH_TEMPERATURE',
                    'metric_value': temp,
                    'threshold_value': CRITICAL_TEMP_THRESHOLD,
                    'severity': severity,
                    'alert_timestamp': str(ts)
                })

            # 2. Aggregation Logic
            if key not in device_aggregates:
                device_aggregates[key] = {
                    'device_id': dev_id,
                    'location': loc,
                    'metric_date': date_str,
                    'temperatures': [temp]
                }
            else:
                device_aggregates[key]['temperatures'].append(temp)

        # Calculate final metrics per device/date bucket
        aggregated_metrics = []
        for agg in device_aggregates.values():
            temps = agg['temperatures']
            aggregated_metrics.append({
                'device_id': agg['device_id'],
                'location': agg['location'],
                'metric_date': agg['metric_date'],
                'avg_temperature': round(sum(temps) / len(temps), 2),
                'max_temperature': max(temps),
                'min_temperature': min(temps),
                'total_readings': len(temps)
            })

        logging.info("Transformation complete. Aggregated %d metrics, detected %d alerts.",
                     len(aggregated_metrics), len(alerts))

        return {
            "aggregated_metrics": aggregated_metrics,
            "alerts": alerts,
            "processed_ids": processed_ids
        }

    @task(task_id='load_processed_telemetry')
    def load_telemetry(transformed_data: Dict[str, Any]) -> str:
        """
        Load Step:
        1. Upserts aggregated metrics into `daily_sensor_metrics`.
        2. Inserts high-temp alerts into `sensor_alerts`.
        3. Flags source records in `raw_sensor_readings` as processed = TRUE.
        """
        aggregated_metrics = transformed_data.get("aggregated_metrics", [])
        alerts = transformed_data.get("alerts", [])
        processed_ids = transformed_data.get("processed_ids", [])

        if not processed_ids:
            return "No data to load."

        pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        conn = pg_hook.get_conn()
        cursor = conn.cursor()

        try:
            # 1. Upsert Daily Aggregated Metrics
            upsert_metric_sql = """
                INSERT INTO daily_sensor_metrics (device_id, location, metric_date, avg_temperature, max_temperature, min_temperature, total_readings)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (device_id, metric_date) DO UPDATE SET
                    avg_temperature = EXCLUDED.avg_temperature,
                    max_temperature = GREATEST(daily_sensor_metrics.max_temperature, EXCLUDED.max_temperature),
                    min_temperature = LEAST(daily_sensor_metrics.min_temperature, EXCLUDED.min_temperature),
                    total_readings = daily_sensor_metrics.total_readings + EXCLUDED.total_readings,
                    calculated_at = CURRENT_TIMESTAMP;
            """
            for metric in aggregated_metrics:
                cursor.execute(upsert_metric_sql, (
                    metric['device_id'],
                    metric['location'],
                    metric['metric_date'],
                    metric['avg_temperature'],
                    metric['max_temperature'],
                    metric['min_temperature'],
                    metric['total_readings']
                ))

            # 2. Insert Sensor Alerts
            insert_alert_sql = """
                INSERT INTO sensor_alerts (reading_id, device_id, alert_type, metric_value, threshold_value, severity)
                VALUES (%s, %s, %s, %s, %s, %s);
            """
            for alert in alerts:
                cursor.execute(insert_alert_sql, (
                    alert['reading_id'],
                    alert['device_id'],
                    alert['alert_type'],
                    alert['metric_value'],
                    alert['threshold_value'],
                    alert['severity']
                ))

            # 3. Mark Raw Records as Processed
            update_raw_sql = """
                UPDATE raw_sensor_readings
                SET processed = TRUE
                WHERE reading_id = ANY(%s);
            """
            cursor.execute(update_raw_sql, (processed_ids,))

            conn.commit()
            logging.info("Database load succeeded. Marked %d records processed.", len(processed_ids))
            return f"Successfully processed {len(processed_ids)} records."

        except Exception as e:
            conn.rollback()
            logging.error("Failed to load telemetry data: %s", str(e))
            raise
        finally:
            cursor.close()
            conn.close()

    # Define Taskflow Execution Dependency Graph
    raw_data = extract_telemetry()
    transformed_data = transform_telemetry(raw_data)
    load_telemetry(transformed_data)


# Instantiate the DAG
iot_dag = iot_telemetry_etl_pipeline()
