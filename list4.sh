export COMMAND='hostname ; pgrep -x -f "python cap.py" -a ; vcgencmd measure_temp; cat /sys/block/mmcblk0/device/serial ; cat /sys/block/mmcblk0/device/cid ; cat /proc/cpuinfo | grep Serial | cut -d " " -f 2 ; cat /sys/class/net/eth0/address ; cat /sys/class/net/wlan0/address'

for i in 2226 2227 2228 2229
do
    echo "$i"
    ssh pi@80.86.151.47 -p $i $COMMAND
done
echo 'all done'

