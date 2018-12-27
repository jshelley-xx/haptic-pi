systemctl stop haptic-pi
systemctl disable haptic-pi
rm /lib/systemd/system/haptic-pi.service
systemctl daemon-reload
systemctl reset-failed
