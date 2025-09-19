# clone
git clone https://github.com/volodmrr/tg_mirror_bot.git
cd tg_mirror_bot

# create .env
cp .env.example .env
nano .env

# setup project
apt install python3.12-venv
./venv/bin/pip install --upgrade pip
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

# create service file
sudo touch /etc/systemd/system/telegram-mirror.service
sudo nano /etc/systemd/system/telegram-mirror.service

# create session
./venv/bin/python3 main.py

# start service
sudo systemctl daemon-reload
sudo systemctl enable telegram-mirror
sudo systemctl restart telegram-mirror
sudo systemctl status telegram-mirror
journalctl -u telegram-mirror -f

# stop service 
sudo systemctl stop telegram-mirror

# disable auto-run on boot
sudo systemctl disable telegram-mirror

# kill process after ^Z
ps aux | grep main.py
kill -9 #<PID>
rm -f mirror_session.session-journal mirror_session.session-shm mirror_session.session-wal