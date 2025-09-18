#!/bin/bash
set -e

APP_NAME="telegram-mirror"
APP_DIR=$(pwd)     # use current repo directory
USER_NAME=$(whoami) # run as current user

echo ">>> Updating system..."
sudo apt update && sudo apt upgrade -y

echo ">>> Installing basics..."
sudo apt install -y python3 python3-venv python3-pip git curl nano

echo ">>> Setting up virtualenv..."
python3 -m venv venv
./venv/bin/pip install --upgrade pip
if [ -f requirements.txt ]; then
  ./venv/bin/pip install -r requirements.txt
else
  ./venv/bin/pip install telethon python-dotenv
fi

echo ">>> Creating systemd service..."
SERVICE_FILE="/etc/systemd/system/$APP_NAME.service"
sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=Telegram Mirror Service
After=network.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$APP_DIR
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/python $APP_DIR/mirror.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo ">>> Reloading systemd and enabling service..."
sudo systemctl daemon-reload
sudo systemctl enable $APP_NAME
sudo systemctl restart $APP_NAME

echo ">>> Done. Service is running."
echo ">>> Check logs with: journalctl -u $APP_NAME -f"
