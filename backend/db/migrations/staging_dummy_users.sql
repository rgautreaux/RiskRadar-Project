-- Staging Dummy User Data for RiskRadar User Security Plan
-- This script inserts anonymized/dummy users for migration testing.

INSERT INTO users (display_name, email, password_hash, zip_code, latitude, longitude, alert_types, notify_severity, created_at, updated_at)
VALUES
  ('Alice Example', 'alice@example.com', '$2b$12$abcdefghijklmnopqrstuv', '90210', 34.0901, -118.4065, '["all"]', 'high', NOW(), NOW()),
  ('Bob Example', 'bob@example.com', '$2b$12$abcdefghijklmnopqrstuv', '10001', 40.7128, -74.0060, '["weather"]', 'medium', NOW(), NOW()),
  ('Carol Example', 'carol@example.com', '$2b$12$abcdefghijklmnopqrstuv', '60601', 41.8837, -87.6233, '["earthquake"]', 'low', NOW(), NOW());

-- Add more dummy users as needed for testing.
