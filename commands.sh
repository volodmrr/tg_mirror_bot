# clone
git clone https://github.com/volodmrr/tg_mirror_bot.git
cd tg_mirror_bot

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
apt install python3.12-venv
./venv/bin/pip install --upgrade pip
python3 -m venv venv
./venv/bin/pip install -r requirements.txt


# create service file
sudo touch $SERVICE_FILE
sudo nano /etc/systemd/system/$APP_NAME.service

# create session
./venv/bin/python3 main.py

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