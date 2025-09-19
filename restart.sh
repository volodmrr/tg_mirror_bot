sudo systemctl daemon-reload
sudo systemctl enable telegram-mirror
sudo systemctl restart telegram-mirror
sudo systemctl status telegram-mirror
journalctl -u telegram-mirror -f