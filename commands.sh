
# create .env
cp .env.example .env
nano .env

# set env
set -e

APP_NAME="telegram-mirror"
APP_DIR=$(pwd)    
USER_NAME=$(whoami) 
SERVICE_FILE="/etc/systemd/system/$APP_NAME.service"

# setup project
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt


# create service file
sudo touch $SERVICE_FILE
sudo nano /etc/systemd/system/$APP_NAME.service

# start service
sudo systemctl daemon-reload
sudo systemctl enable $APP_NAME
sudo systemctl restart $APP_NAME


# check status
sudo systemctl status $APP_NAME

# check logs
journalctl -u $APP_NAME -f

# stop service 
sudo systemctl stop $APP_NAME

# disable auto-run on boot
sudo systemctl disable $APP_NAME