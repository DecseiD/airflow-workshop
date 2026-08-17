CREATE TABLE IF NOT EXISTS sensor_maintenance_queue (
  ticket_id SERIAL PRIMARY KEY,
  device_id VARCHAR(50) NOT NULL,
  location VARCHAR(100) NOT NULL,
  current_temp NUMERIC(5,2) NOT NULL,
  risk_level VARCHAR(20) NOT NULL,
  priority_score INT NOT NULL,
  recommended_action TEXT NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'OPEN',
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
