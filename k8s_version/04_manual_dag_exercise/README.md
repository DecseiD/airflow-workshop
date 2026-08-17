# 04_manual_dag_exercise — AKS

This module adds a manual classification DAG that creates maintenance tickets from high-risk sensor readings.

## Steps

1. Apply schema:

```bash
kubectl cp init_maintenance_schema.sql airflow/iot-telemetry-db-0:/tmp/init_maintenance_schema.sql
kubectl exec -n airflow iot-telemetry-db-0 -- psql -U iot_user -d iot_telemetry -f /tmp/init_maintenance_schema.sql
```

2. Copy DAG file to the scheduler DAG path (or use your DAG sync source):

```bash
SCHED=$(kubectl get pod -n airflow -l component=scheduler -o jsonpath='{.items[0].metadata.name}')
kubectl cp dags/manual_sensor_cleaning_dag.py airflow/$SCHED:/opt/airflow/dags/manual_sensor_cleaning_dag.py
```

3. Trigger DAG `manual_sensor_maintenance_classifier`.

4. Verify queue table:

```sql
SELECT ticket_id, device_id, risk_level, priority_score, status
FROM sensor_maintenance_queue
ORDER BY priority_score DESC;
```
