-- Schema Update for Module 04: Manual DAG Creation Exercise
-- Creates the target Maintenance Queue table in iot_telemetry database

DROP TABLE IF EXISTS sensor_maintenance_queue;

CREATE TABLE sensor_maintenance_queue (
    ticket_id SERIAL PRIMARY KEY,
    device_id VARCHAR(50) NOT NULL,
    location VARCHAR(100) NOT NULL,
    current_temp NUMERIC(5, 2) NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    priority_score INT NOT NULL,
    recommended_action VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'OPEN'
);
