#!/bin/bash

# Create base directories
mkdir -p grafana/provisioning/{dashboards,datasources}
mkdir -p grafana/dashboards

# Create dashboard provisioning configuration
cat > grafana/provisioning/dashboards/dashboard.yml << 'EOL'
apiVersion: 1

providers:
  - name: 'Default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
EOL

# Create datasource provisioning configuration for PostgreSQL
cat > grafana/provisioning/datasources/datasource.yml << 'EOL'
apiVersion: 1

datasources:
  - name: PostgreSQL
    type: postgres
    url: postgres:5432
    user: myuser
    secureJsonData:
      password: mypassword
    jsonData:
      database: frauddb
      sslmode: disable
      maxOpenConns: 100
      maxIdleConns: 100
      maxIdleConnsAuto: true
      connMaxLifetime: 14400
      postgresVersion: 1200
      timescaledb: false
EOL

# Create an example dashboard
cat > grafana/dashboards/example-dashboard.json << 'EOL'
{
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": {
          "type": "grafana",
          "uid": "-- Grafana --"
        },
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations & Alerts",
        "type": "dashboard"
      }
    ]
  },
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 0,
  "id": 1,
  "title": "Fraud Detection Dashboard",
  "uid": "fraud-detection",
  "version": 1,
  "panels": []
}
EOL

# Set appropriate permissions
chmod 755 grafana/provisioning/dashboards/dashboard.yml
chmod 755 grafana/provisioning/datasources/datasource.yml
chmod 644 grafana/dashboards/example-dashboard.json

echo "Grafana provisioning structure has been created successfully."
echo "Directory structure:"
