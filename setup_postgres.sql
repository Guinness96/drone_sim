-- Create drone_monitoring_db database
CREATE DATABASE drone_monitoring_db;

-- Create drone_user with password
CREATE USER drone_user WITH PASSWORD 'drone_password';

-- Grant privileges to drone_user on drone_monitoring_db
GRANT ALL PRIVILEGES ON DATABASE drone_monitoring_db TO drone_user;

-- Connect to the drone_monitoring_db to grant schema privileges
\c drone_monitoring_db

-- Grant schema privileges to drone_user
ALTER DEFAULT PRIVILEGES GRANT ALL ON TABLES TO drone_user; 