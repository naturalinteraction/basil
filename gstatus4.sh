export COMMAND='hostname ; cd /home/pi/basil ; pwd ; git status'

for i in 2226 2227 2228 2229
do
    echo "$i"
    ssh pi@80.86.151.47 -p $i $COMMAND
done
echo 'all done'
