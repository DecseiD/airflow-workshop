"""
===============================================================================
Module 04 Exercise DAG: manual_sensor_maintenance_classifier
Description: Live workshop exercise DAG. Extracts raw sensor telemetry from 
             the existing PostgreSQL database, classifies device maintenance risk, 
             and writes actionable maintenance tickets into sensor_maintenance_queue.
===============================================================================
"""

from datetime import datetime, timedelta
import logging
from typing import Dict, List, Any

from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook

POSTGRES_CONN_ID = 'iot_db_conn'

DEFAULT_ARGS = {
    'owner': 'workshop_participant',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=30),
}


@dag(
    dag_id='manual_sensor_maintenance_classifier',
    default_args=DEFAULT_ARGS,
    description='Module 04 Exercise: Classifies IoT devices into maintenance queues based on live telemetry',
    schedule_interval=None, # Manual trigger only for live workshop showcase
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['workshop', 'module04', 'exercise', 'taskflow'],
)
def manual_maintenance_pipeline():
    """
    Exercise DAG pipeline demonstrating manual DAG deployment and visible DB state change.
    """

    @task(task_id='extract_telemetry_for_maintenance')
    def extract_telemetry() -> List[Dict[str, Any]]:
        """
        Step 1: Connect to existing PostgreSQL database and fetch telemetry records.
        """
        logging.info("Connecting to PostgreSQL via PostgresHook: %s", POSTGRES_CONN_ID)
        pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)

        sql = """
            SELECT reading_id, device_id, location, temperature_celsius, battery_pct
            FROM raw_sensor_readings;
        """
        
        conn = pg_hook.get_conn()
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]
        records = [dict(zip(colnames, row)) for row in rows]
        
        cursor.close()
        conn.close()

        logging.info("Fetched %d telemetry records for maintenance classification.", len(records))
        return records

    @task(task_id='classify_device_risk')
    def classify_risk(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Step 2: Business Logic Transformation - Classify device maintenance risk based on temp & battery.
        """
        tickets = []
        for r in records:
            dev_id = r['device_id']
            loc = r['location']
            temp = float(r['temperature_celsius'])
            battery = float(r['battery_pct'])

            # Risk Classification Logic
            if temp >= 85.0:
                risk_level = 'CRITICAL'
                priority_score = 100
                action = 'CRITICAL DISPATCH: Emergency Cooling Unit Replacement Required'
            elif temp >= 75.0:
                risk_level = 'HIGH'
                priority_score = 75
                action = 'HIGH PRIORITY: HVAC Filter & Duct Inspection'
            elif battery < 80.0:
                risk_level = 'MEDIUM'
                priority_score = 50
                action = 'BATTERY MAINTENANCE: Low Battery Cell Replacement'
            else:
                risk_level = 'NORMAL'
                priority_score = 10
                action = 'ROUTINE MONITORING: System Nominal'

            tickets.append({
                'device_id': dev_id,
                'location': loc,
                'current_temp': temp,
                'risk_level': risk_level,
                'priority_score': priority_score,
                'recommended_action': action
            })

        logging.info("Classified %d maintenance tickets.", len(tickets))
        return tickets

    @task(task_id='populate_maintenance_queue')
    def load_tickets(tickets: List[Dict[str, Any]]) -> str:
        """
        Step 3: Load Step - Writes maintenance tickets into sensor_maintenance_queue.
        """
        if not tickets:
            return "No tickets to load."

        pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        conn = pg_hook.get_conn()
        cursor = conn.cursor()

        insert_sql = """
            INSERT INTO sensor_maintenance_queue 
            (device_id, location, current_temp, risk_level, priority_score, recommended_action)
            VALUES (%s, %s, %s, %s, %s, %s);
        """

        try:
            # Clear existing tickets for clean re-run demonstration
            cursor.execute("TRUNCATE TABLE sensor_maintenance_queue;")

            for t in tickets:
                cursor.execute(insert_sql, (
                    t['device_id'],
                    t['location'],
                    t['current_temp'],
                    t['risk_level'],
                    t['priority_score'],
                    t['recommended_action']
                ))

            conn.commit()
            logging.info("Successfully populated %d tickets into sensor_maintenance_queue.", len(tickets))
            return f"Inserted {len(tickets)} tickets into maintenance queue."

        except Exception as e:
            conn.rollback()
            logging.error("Failed to insert maintenance tickets: %s", str(e))
            raise
        finally:
            cursor.close()
            conn.close()

    # Define DAG workflow graph
    records = extract_telemetry()
    classified_tickets = classify_risk(records)
    load_tickets(classified_tickets)


# Instantiate the DAG
maintenance_dag = manual_maintenance_pipeline()
