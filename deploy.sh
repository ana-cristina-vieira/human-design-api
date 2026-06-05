#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# deploy.sh  —  Human Design API  |  Negócios com ALMA
# Run this script once on your Hostinger VPS to set up and start the service.
# Ubuntu 22.04 LTS assumed.
# ─────────────────────────────────────────────────────────────────────────────

set -e

APP_DIR="/opt/human-design-api"
SERVICE="human-design-api"

echo "=== 1. System dependencies ==="
apt-get update -q
apt-get install -y python3 python3-pip python3-venv python3-dev build-essential git

echo "=== 2. Copy files ==="
mkdir -p "$APP_DIR"
cp -r ./* "$APP_DIR/"
cp .env.example "$APP_DIR/.env" 2>/dev/null || true

echo "=== 3. Python virtual environment ==="
python3 -m venv "$APP_DIR/venv"
source "$APP_DIR/venv/bin/activate"
pip install --upgrade pip
pip install -r "$APP_DIR/requirements.txt"

echo "=== 4. Systemd service ==="
cat > /etc/systemd/system/${SERVICE}.service <<EOF
[Unit]
Description=Human Design API — Negócios com ALMA
After=network.target

[Service]
WorkingDirectory=${APP_DIR}
EnvironmentFile=${APP_DIR}/.env
ExecStart=${APP_DIR}/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3
User=www-data

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable $SERVICE
systemctl restart $SERVICE

echo ""
echo "✓ API running on port 8000"
echo "  Test: curl http://localhost:8000/health"
echo ""
echo "Next: configure nginx reverse proxy and point your domain."
