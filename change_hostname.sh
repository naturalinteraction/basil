sudo raspi-config nonint do_hostname "$@"
cat /etc/hostname
sudo hostname "$@"
hostname
