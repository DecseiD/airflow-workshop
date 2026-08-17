DROP TABLE IF EXISTS sensor_alerts;
DROP TABLE IF EXISTS daily_sensor_metrics;
DROP TABLE IF EXISTS raw_sensor_readings;

CREATE TABLE raw_sensor_readings (
  reading_id SERIAL PRIMARY KEY,
  device_id VARCHAR(50) NOT NULL,
  location VARCHAR(100) NOT NULL,
  temperature_celsius NUMERIC(5,2) NOT NULL,
  humidity_pct NUMERIC(5,2) NOT NULL,
  battery_pct NUMERIC(5,2) NOT NULL,
  reading_timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  processed BOOLEAN DEFAULT FALSE
);

CREATE TABLE daily_sensor_metrics (
  metric_id SERIAL PRIMARY KEY,
  device_id VARCHAR(50) NOT NULL,
  location VARCHAR(100) NOT NULL,
  metric_date DATE NOT NULL,
  avg_temperature NUMERIC(5,2) NOT NULL,
  max_temperature NUMERIC(5,2) NOT NULL,
  min_temperature NUMERIC(5,2) NOT NULL,
  total_readings INT NOT NULL,
  calculated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(device_id, metric_date)
);

CREATE TABLE sensor_alerts (
  alert_id SERIAL PRIMARY KEY,
  reading_id INT REFERENCES raw_sensor_readings(reading_id),
  device_id VARCHAR(50) NOT NULL,
  alert_type VARCHAR(50) NOT NULL,
  metric_value NUMERIC(5,2) NOT NULL,
  threshold_value NUMERIC(5,2) NOT NULL,
  alert_timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  severity VARCHAR(20) NOT NULL
);

INSERT INTO raw_sensor_readings(device_id, location, temperature_celsius, humidity_pct, battery_pct, reading_timestamp)
VALUES
  ('IOT-NODE-ALPHA', 'Server Room A', 22.4, 45.2, 98.0, NOW() - INTERVAL '3 hour'),
  ('IOT-NODE-ALPHA', 'Server Room A', 82.5, 41.0, 97.0, NOW() - INTERVAL '1 hour'),
  ('IOT-NODE-BETA', 'Warehouse North', 18.9, 61.2, 88.0, NOW() - INTERVAL '1 hour'),
  ('IOT-NODE-GAMMA', 'HVAC Plant 01', 78.4, 28.5, 71.5, NOW() - INTERVAL '2 hour');
