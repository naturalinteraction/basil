export COMMAND='cd /home/pi/basil ; ls -l cache'

for i in 46 47 48 49
do
    echo "$i"
    ssh pi@192.168.1.$i $COMMAND
done
echo 'all done'
