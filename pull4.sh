export COMMAND='cd /home/pi/basil ; git pull'

for i in 2226 2227 2228 2229
do
    echo "$i"
    ssh pi@80.86.151.47 -p $i $COMMAND
done
echo 'all done'

